from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article, ApprovedArticleLog, CustomUser, Newsletter, Publisher


class CustomUserAdmin(UserAdmin):
    """
    User admin that exposes the role field so admins can assign roles.
    """

    list_display = ("username", "email", "role", "is_staff")
    list_filter = UserAdmin.list_filter + ("role",)
    fieldsets = UserAdmin.fieldsets + (
        ("Role & subscriptions", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(ApprovedArticleLog)
