"""Forms used throughout the News application."""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class SignUpForm(UserCreationForm):
    """
    Registration form that lets new users pick their role.
    """

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role"]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]


class NewsletterForm(forms.ModelForm):
    """
    Newsletter form that only allows approved articles.
    """

    class Meta:
        model = Newsletter
        fields = ["title", "description", "articles"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["articles"].queryset = Article.objects.filter(
            approved=True
        )


class PublisherForm(forms.ModelForm):
    """
    Publisher form.

    Editors list only shows users with editor role.
    Journalists list only shows users with journalist role.
    Publishers cannot assign themselves.
    """

    class Meta:
        model = Publisher
        fields = ["name", "description", "editors", "journalists"]

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        self.fields["editors"].queryset = CustomUser.objects.filter(
            role="editor"
        )

        self.fields["journalists"].queryset = CustomUser.objects.filter(
            role="journalist"
        )