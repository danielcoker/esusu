from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom persmission to allow only the owner of an object edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (hasattr(obj, 'owner') and obj.owner == request.user) or \
            (hasattr(obj, 'user') and obj.user == request.user)


class IsOwner(BasePermission):
    """
    Custom permission to allow only the owner of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        return (hasattr(obj, 'owner') and obj.owner == request.user) or \
            (hasattr(obj, 'user') and obj.user == request.user)
