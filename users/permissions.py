from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Employee').exists()
    
class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='User').exists()
    
class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
           return True
       
        return obj.owner == request.user