from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for custom users.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for publishers.
    """

    class Meta:
        model = Publisher
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for articles with defensive validation.
    """

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_name",
            "created_at",
            "approved",
            "publisher",
        ]

        read_only_fields = [
            "author",
            "approved",
            "created_at",
        ]

    def validate_title(self, value):
        """
        Validate that the title is meaningful.
        """

        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "The article title must be at least 5 characters long."
            )

        return value.strip()

    def validate_content(self, value):
        """
        Validate that article content is not empty.
        """

        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "The article content must be at least 20 characters long."
            )

        return value.strip()


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletters.
    """

    class Meta:
        model = Newsletter
        fields = "__all__"
        read_only_fields = ["author", "created_at"]

    def validate_title(self, value):
        """
        Validate newsletter title.
        """

        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "The newsletter title must be at least 5 characters long."
            )

        return value.strip()