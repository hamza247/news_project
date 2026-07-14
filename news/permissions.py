from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):
    """
    Allows access only to users with the journalist role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "journalist"
        )


class IsEditor(BasePermission):
    """
    Allows access only to users with the editor role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "editor"
        )


class IsEditorOrJournalist(BasePermission):
    """
    Allows access to editors and journalists only.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["editor", "journalist"]
        )