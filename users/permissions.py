from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Employee').exists()
    
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='User').exists()