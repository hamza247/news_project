from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),

    path("subscriptions/", views.subscriptions, name="subscriptions"),
    path("articles/new/", views.create_article, name="create_article"),
    path("newsletters/new/", views.create_newsletter, name="create_newsletter"),
    path("editor/review/", views.review_articles, name="review_articles"),
    path(
        "editor/approve/<int:article_id>/",
        views.approve_article,
        name="approve_article",
    ),

    path("publishers/new/", views.create_publisher, name="create_publisher"),
    path(
        "publishers/<int:pk>/edit/",
        views.edit_publisher,
        name="edit_publisher",
    ),

    path("api/token/", obtain_auth_token, name="api_token"),
    path("api/approved/", views.approved_article_log_api, name="approved_api"),
    path("api/articles/", views.ArticleListCreateApi.as_view(), name="api_articles"),
    path(
        "api/articles/subscribed/",
        views.SubscribedArticlesApi.as_view(),
        name="api_subscribed_articles",
    ),
    path(
        "api/articles/<int:article_id>/",
        views.ArticleDetailApi.as_view(),
        name="api_article_detail",
    ),
    path(
        "api/newsletters/",
        views.NewsletterListCreateApi.as_view(),
        name="api_newsletters",
    ),
    path(
    "articles/<int:article_id>/edit/",
    views.edit_article,
    name="edit_article",
    ),
    path(
        "articles/<int:article_id>/delete/",
        views.delete_article,
        name="delete_article",
    ),
]
