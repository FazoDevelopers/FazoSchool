from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser,IsAuthenticatedOrReadOnly,BasePermission

class TasischiPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="admin":
            if user.admin.types.slug=="tasischi":
                return True
            return False
        else:
            return False

class TasischiOrManagerPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="admin":
            if user.admin.types.slug=="tasischi" or user.admin.types.slug=="manager":
                return True
            return False
        else:
            return False
