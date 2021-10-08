from rest_framework import permissions

from ..utils import in_res_crud_group



class ResCRUDOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif in_res_crud_group(request.user):
            return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        elif in_res_crud_group(request.user):
            return True


