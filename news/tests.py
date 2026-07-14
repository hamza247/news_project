from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Article, ApprovedArticleLog, Newsletter, Publisher
from .views import notify_subscribers

User = get_user_model()


class NewsApiTests(TestCase):
    """Automated tests for the news application REST API."""

    def setUp(self):
        self.client = APIClient()

        self.reader = User.objects.create_user(
            username="reader",
            password="pass12345",
            role="reader",
            email="reader@example.com",
        )

        self.journalist = User.objects.create_user(
            username="journalist",
            password="pass12345",
            role="journalist",
            email="journalist@example.com",
        )

        self.editor = User.objects.create_user(
            username="editor",
            password="pass12345",
            role="editor",
            email="editor@example.com",
        )

        self.publisher = Publisher.objects.create(
            name="Tech Daily",
            description="Technology news publication.",
        )

        self.publisher.journalists.add(self.journalist)
        self.publisher.editors.add(self.editor)

        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        self.approved_article = Article.objects.create(
            title="Approved Article",
            content="This is an approved article with enough content.",
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
        )

        self.unapproved_article = Article.objects.create(
            title="Draft Article",
            content="This is a draft article with enough content.",
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )

        self.reader_token = Token.objects.create(user=self.reader)
        self.journalist_token = Token.objects.create(user=self.journalist)
        self.editor_token = Token.objects.create(user=self.editor)

    def authenticate(self, token):
        """Attach token authentication credentials to the API client."""

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_reader_can_get_approved_articles(self):
        self.authenticate(self.reader_token)

        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Approved Article")

    def test_reader_can_get_subscribed_articles(self):
        self.authenticate(self.reader_token)

        response = self.client.get("/api/articles/subscribed/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_journalist_can_create_article(self):
        self.authenticate(self.journalist_token)

        payload = {
            "title": "New Journalist Article",
            "content": "This is valid content for a new article.",
            "publisher": self.publisher.id,
        }

        response = self.client.post("/api/articles/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data["approved"])

    def test_reader_cannot_create_article(self):
        self.authenticate(self.reader_token)

        payload = {
            "title": "Invalid Article",
            "content": "This request should fail for a reader.",
            "publisher": self.publisher.id,
        }

        response = self.client.post("/api/articles/", payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_reader_cannot_view_unapproved_article(self):
        self.authenticate(self.reader_token)

        response = self.client.get(
            f"/api/articles/{self.unapproved_article.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_can_delete_article(self):
        self.authenticate(self.editor_token)

        response = self.client.delete(
            f"/api/articles/{self.approved_article.id}/"
        )

        self.assertEqual(response.status_code, 204)

    def test_newsletter_can_be_created_by_journalist(self):
        self.authenticate(self.journalist_token)

        payload = {
            "title": "Weekly Tech",
            "description": "A weekly technology newsletter.",
            "articles": [self.approved_article.id],
        }

        response = self.client.post("/api/newsletters/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Weekly Tech")
        self.assertEqual(Newsletter.objects.count(), 1)

    def test_notify_subscribers_sends_email(self):
        notify_subscribers(self.approved_article)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Approved Article", mail.outbox[0].subject)

    def test_approved_article_log_api(self):
        payload = {
            "article": self.approved_article.id,
            "title": self.approved_article.title,
        }

        response = self.client.post("/api/approved/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ApprovedArticleLog.objects.count(), 1)

    def test_article_validation_rejects_short_title(self):
        self.authenticate(self.journalist_token)

        payload = {
            "title": "Bad",
            "content": "This content is long enough to pass validation.",
            "publisher": self.publisher.id,
        }

        response = self.client.post("/api/articles/", payload, format="json")

        self.assertEqual(response.status_code, 400)