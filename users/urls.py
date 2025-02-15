"""
URL configuration for PackRunner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView
from .views import LoginView, LogoutView, UserListView, UserDetailView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/', UserListView.as_view()),
    path('users/<int:id>/', UserDetailView.as_view()),
    
    # user profile
    path('profile/', UserProfileView.as_view())
]
