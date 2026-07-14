"""Models used by the News application."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model with role-based access.

    Roles:
    - reader: can view approved articles and newsletters.
    - journalist: can create articles and newsletters.
    - editor: can review, approve, update, and delete content.
    - publisher: can create and manage publications.
    """

    READER = "reader"
    EDITOR = "editor"
    JOURNALIST = "journalist"
    PUBLISHER = "publisher"

    ROLE_CHOICES = [
        (READER, "Reader"),
        (EDITOR, "Editor"),
        (JOURNALIST, "Journalist"),
        (PUBLISHER, "Publisher"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER,
    )

    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        blank=True,
        related_name="subscribed_readers",
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="journalist_subscribers",
    )

    def save(self, *args, **kwargs):
        """
        Save the user and automatically assign the correct Django group
        based on the selected role.
        """
        super().save(*args, **kwargs)

        role_to_group = {
            self.READER: "Reader",
            self.EDITOR: "Editor",
            self.JOURNALIST: "Journalist",
            self.PUBLISHER: "Publisher",
        }

        group_name = role_to_group.get(self.role)

        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.clear()
            self.groups.add(group)

    def __str__(self):
        return self.username


class Publisher(models.Model):
    """
    Represents a curated news publication.

    A publisher can have multiple editors and journalists.
    """

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="editor_publishers",
    )

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="journalist_publishers",
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Represents a news article.

    Articles are created by journalists and must be approved by
    an editor before being visible to readers.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Represents a newsletter created by journalists or editors.

    A newsletter can contain many approved articles.
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="newsletters",
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ApprovedArticleLog(models.Model):
    """
    Logs approved articles that were posted to the internal API.
    """

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="approval_logs",
    )

    title = models.CharField(max_length=200)
    approved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title