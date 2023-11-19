from rest_framework.permissions import BasePermission,IsAuthenticatedOrReadOnly

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
        
class TasischiOrFinancePermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="admin":
            if user.admin.types.slug=="tasischi" or user.admin.types.slug=="finance":
                return True
            return False
        else:
            return False
        
class TasischiOrManagerOrAdminPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="admin":
            if user.admin.types.slug=="tasischi" or user.admin.types.slug=="manager" or user.admin.types.slug=="admin":
                return True
            return False
        else:
            return False

class TeacherPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="teacher":
            return True
        else:
            return False
        
class StudentPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="student":
            return True
        else:
            return False
        
class ParentPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated and user.type_user=="parent":
            return True
        else:
            return False
