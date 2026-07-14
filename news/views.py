import requests

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ArticleForm, NewsletterForm, PublisherForm, SignUpForm
from .models import (
    Article,
    ApprovedArticleLog,
    CustomUser,
    Newsletter,
    Publisher,
)
from .serializers import ArticleSerializer, NewsletterSerializer


def register(request):
    """
    Register a new user, log them in, and send them to their dashboard.
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "news/register.html", {"form": form})


@login_required
def dashboard(request):
    """
    Route each user to a role-specific dashboard showing only the
    functionality their role permits.
    """

    role = request.user.role

    if role == "journalist":
        articles = request.user.articles.order_by("-created_at")
        newsletters = request.user.newsletters.order_by("-created_at")
        return render(
            request,
            "news/dashboard_journalist.html",
            {"articles": articles, "newsletters": newsletters},
        )

    if role == "editor":
        pending = Article.objects.filter(approved=False).order_by("-created_at")
        newsletters = Newsletter.objects.order_by("-created_at")
        return render(
            request,
            "news/dashboard_editor.html",
            {"pending_articles": pending, "newsletters": newsletters},
        )

    if role == "publisher":
        publications = Publisher.objects.filter(
            editors=request.user,
        ) | Publisher.objects.filter(journalists=request.user)
        return render(
            request,
            "news/dashboard_publisher.html",
            {"publications": publications.distinct()},
        )

    # Default: reader.
    articles = Article.objects.filter(approved=True).order_by("-created_at")
    newsletters = Newsletter.objects.order_by("-created_at")
    return render(
        request,
        "news/dashboard_reader.html",
        {"articles": articles, "newsletters": newsletters},
    )


@login_required
def subscriptions(request):
    """
    Let readers subscribe to / unsubscribe from publishers and journalists.
    """

    if request.user.role != "reader":
        return redirect("dashboard")

    if request.method == "POST":
        target = request.POST.get("target")
        obj_id = request.POST.get("id")
        action = request.POST.get("action")

        if target == "publisher":
            publisher = get_object_or_404(Publisher, id=obj_id)
            relation = request.user.subscribed_publishers
            label = publisher.name
        else:
            journalist = get_object_or_404(
                CustomUser, id=obj_id, role="journalist"
            )
            relation = request.user.subscribed_journalists
            label = journalist.username

        if action == "subscribe":
            relation.add(obj_id)
            messages.success(request, f"Subscribed to {label}.")
        else:
            relation.remove(obj_id)
            messages.success(request, f"Unsubscribed from {label}.")

        return redirect("subscriptions")

    subscribed_publisher_ids = set(
        request.user.subscribed_publishers.values_list("id", flat=True)
    )
    subscribed_journalist_ids = set(
        request.user.subscribed_journalists.values_list("id", flat=True)
    )

    publishers = [
        {"obj": publisher, "subscribed": publisher.id in subscribed_publisher_ids}
        for publisher in Publisher.objects.order_by("name")
    ]
    journalists = [
        {"obj": journalist, "subscribed": journalist.id in subscribed_journalist_ids}
        for journalist in CustomUser.objects.filter(role="journalist").order_by(
            "username"
        )
    ]

    return render(
        request,
        "news/subscriptions.html",
        {"publishers": publishers, "journalists": journalists},
    )


@login_required
def create_article(request):
    """
    Allow journalists to create articles.

    Articles are saved as unapproved until reviewed by an editor.
    """

    if request.user.role != "journalist":
        return redirect("dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            messages.success(request, "Article submitted for review.")
            return redirect("dashboard")
    else:
        form = ArticleForm()

    return render(request, "news/article_form.html", {"form": form})

@login_required
def edit_article(request, article_id):
    """
    Allow journalists to edit their own articles
    and editors to edit any article.
    """

    article = get_object_or_404(Article, id=article_id)

    if request.user.role == "journalist" and article.author != request.user:
        return redirect("dashboard")

    if request.user.role not in ["journalist", "editor"]:
        return redirect("dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            form.save()
            messages.success(request, "Article updated successfully.")
            return redirect("dashboard")
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "news/article_form.html",
        {"form": form},
    )


@login_required
def delete_article(request, article_id):
    """
    Allow journalists to delete their own articles
    and editors to delete any article.
    """

    article = get_object_or_404(Article, id=article_id)

    if request.user.role == "journalist" and article.author != request.user:
        return redirect("dashboard")

    if request.user.role not in ["journalist", "editor"]:
        return redirect("dashboard")

    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted successfully.")
        return redirect("dashboard")

    return render(
        request,
        "news/delete_article.html",
        {"article": article},
    )
    
@login_required
def create_newsletter(request):
    """
    Allow journalists and editors to create newsletters.
    """

    if request.user.role not in ["journalist", "editor"]:
        return redirect("dashboard")

    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()
            messages.success(request, "Newsletter created.")
            return redirect("dashboard")
    else:
        form = NewsletterForm()

    return render(request, "news/newsletter_form.html", {"form": form})


@login_required
def review_articles(request):
    """
    Allow editors to view articles waiting for approval.
    """

    if request.user.role != "editor":
        return redirect("dashboard")

    articles = Article.objects.filter(approved=False)
    return render(request, "news/review_articles.html", {"articles": articles})


def notify_subscribers(article):
    """
    Email an approved article to subscribed readers.

    Subscribers may follow the article publisher or journalist.
    """

    subscribers = set()

    if article.publisher:
        publisher_readers = article.publisher.subscribed_readers.all()

        for reader in publisher_readers:
            if reader.email:
                subscribers.add(reader.email)

    journalist_readers = article.author.journalist_subscribers.all()

    for reader in journalist_readers:
        if reader.email:
            subscribers.add(reader.email)

    if subscribers:
        send_mail(
            subject=f"New approved article: {article.title}",
            message=article.content,
            from_email="noreply@example.com",
            recipient_list=list(subscribers),
            fail_silently=True,
        )


def log_approved_article(article, request):
    """
    Log approved articles to the internal REST API.

    If the request fails, a local database log is created instead.
    """

    api_url = request.build_absolute_uri("/api/approved/")

    payload = {
        "article": article.id,
        "title": article.title,
    }

    try:
        requests.post(api_url, json=payload, timeout=5)
    except requests.RequestException:
        ApprovedArticleLog.objects.create(
            article=article,
            title=article.title,
        )


@login_required
def approve_article(request, article_id):
    """
    Allow editors to approve articles.

    After approval:
    - subscribers receive an email
    - the approved article is logged to the internal API
    """

    if request.user.role != "editor":
        return redirect("dashboard")

    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        article.approved = True
        article.save()

        notify_subscribers(article)
        log_approved_article(article, request)

        messages.success(request, f"Approved “{article.title}”.")
        return redirect("review_articles")

    return render(request, "news/approve_article.html", {"article": article})


@login_required
def create_publisher(request):
    """
    Allow publishers to create a new publication.
    """

    if request.user.role != "publisher":
        return redirect("dashboard")

    if request.method == "POST":
        form = PublisherForm(request.POST, current_user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Publication created.")
            return redirect("dashboard")
    else:
        form = PublisherForm(current_user=request.user)

    return render(
        request,
        "news/publisher_form.html",
        {"form": form, "heading": "Create Publication"},
    )


@login_required
def edit_publisher(request, pk):
    """
    Allow publishers to edit an existing publication.
    """

    if request.user.role != "publisher":
        return redirect("dashboard")

    publisher = get_object_or_404(Publisher, pk=pk)

    if request.method == "POST":
        form = PublisherForm(
            request.POST, 
            instance=publisher, 
            current_user=request.user,
            )

        if form.is_valid():
            form.save()
            messages.success(request, "Publication updated.")
            return redirect("dashboard")
    else:
        form = PublisherForm(
        instance=publisher,
        current_user=request.user,
        )

    return render(
        request,
        "news/publisher_form.html",
        {"form": form, "heading": f"Edit {publisher.name}"},
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def approved_article_log_api(request):
    """
    Internal API endpoint that logs approved articles.
    """

    article_id = request.data.get("article")
    title = request.data.get("title")

    if not article_id or not title:
        return Response(
            {"error": "Both article and title are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    article = get_object_or_404(Article, id=article_id)

    log = ApprovedArticleLog.objects.create(
        article=article,
        title=title,
    )

    return Response(
        {
            "id": log.id,
            "article": article.id,
            "title": log.title,
        },
        status=status.HTTP_201_CREATED,
    )

class ArticleListCreateApi(APIView):
    """
    GET: return approved articles.
    POST: allow journalists to create articles.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        articles = Article.objects.filter(approved=True)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != "journalist":
            return Response(
                {"error": "Only journalists can create articles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ArticleSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save(author=request.user, approved=False)
            except Exception as error:
                return Response(
                    {"error": str(error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribedArticlesApi(APIView):
    """
    Return only articles from the reader's subscribed publishers or journalists.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        publisher_ids = request.user.subscribed_publishers.values_list(
            "id",
            flat=True,
        )

        journalist_ids = request.user.subscribed_journalists.values_list(
            "id",
            flat=True,
        )

        publisher_articles = Article.objects.filter(
            approved=True,
            publisher_id__in=publisher_ids,
        )

        journalist_articles = Article.objects.filter(
            approved=True,
            author_id__in=journalist_ids,
        )

        articles = (publisher_articles | journalist_articles).distinct()
        serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data)


class ArticleDetailApi(APIView):
    """
    Retrieve, update, or delete a single article.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_article(self, article_id):
        """
        Safely retrieve article or return 404.
        """

        return get_object_or_404(Article, id=article_id)

    def get(self, request, article_id):
        article = self.get_article(article_id)

        if request.user.role == "reader" and not article.approved:
            return Response(
                {"error": "Readers can only view approved articles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, article_id):
        article = self.get_article(article_id)

        if request.user.role not in ["editor", "journalist"]:
            return Response(
                {"error": "Only editors or journalists can update articles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.role == "journalist" and article.author != request.user:
            return Response(
                {"error": "Journalists can only update their own articles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ArticleSerializer(
            article,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as error:
                return Response(
                    {"error": str(error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, article_id):
        article = self.get_article(article_id)

        if request.user.role not in ["editor", "journalist"]:
            return Response(
                {"error": "Only editors or journalists can delete articles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.role == "journalist" and article.author != request.user:
            return Response(
                {"error": "Journalists can only delete their own articles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewsletterListCreateApi(APIView):
    """
    GET: return newsletters.
    POST: allow journalists and editors to create newsletters.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        newsletters = Newsletter.objects.all()
        serializer = NewsletterSerializer(newsletters, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role not in ["journalist", "editor"]:
            return Response(
                {
                    "error": (
                        "Only journalists or editors can create newsletters."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NewsletterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save(author=request.user)
            except Exception as error:
                return Response(
                    {"error": str(error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)