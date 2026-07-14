from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Create default user groups and assign their permissions.
    """

    help = "Create user groups and assign permissions."

    def handle(self, *args, **kwargs):
        reader_group, _ = Group.objects.get_or_create(name="Reader")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        journalist_group, _ = Group.objects.get_or_create(name="Journalist")
        publisher_group, _ = Group.objects.get_or_create(name="Publisher")

        view_permissions = Permission.objects.filter(codename__startswith="view_")
        editor_permissions = Permission.objects.filter(
            codename__in=[
                "view_article",
                "change_article",
                "delete_article",
                "view_newsletter",
                "change_newsletter",
                "delete_newsletter",
            ]
        )
        journalist_permissions = Permission.objects.filter(
            codename__in=[
                "add_article",
                "view_article",
                "change_article",
                "delete_article",
                "add_newsletter",
                "view_newsletter",
                "change_newsletter",
                "delete_newsletter",
            ]
        )
        publisher_permissions = Permission.objects.filter(
            codename__in=[
                "add_publisher",
                "view_publisher",
                "change_publisher",
                "delete_publisher",
                "view_article",
                "view_newsletter",
            ]
        )

        reader_group.permissions.set(view_permissions)
        editor_group.permissions.set(editor_permissions)
        journalist_group.permissions.set(journalist_permissions)
        publisher_group.permissions.set(publisher_permissions)

        self.stdout.write(self.style.SUCCESS("Groups created successfully."))
