from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .permissions import *

# Register API
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print(serializer)
        print(user.is_active)
        group_name = request.data.get("group", "User")  
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        return Response({
            "message": "User registered successfully!", 
            "data": serializer.data
        })

# Login API
class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            raise AuthenticationFailed("Phone number and password are required!")

        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        refresh = RefreshToken.for_user(user)
        token_data = MyTokenObtainPairSerializer.get_token(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "groups": token_data["groups"],
            "permissions": token_data["permissions"],
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'message': 'Refresh token is required'}, status=400)
        try:
            if refresh_token.startswith("Bearer "):
                refresh_token = refresh_token[7:]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Successfully logged out.'}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)
        
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many = True)
        return Response({"message": "Successfully", "data": serializer.data })
        
class UserDetailView(APIView):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = UserSerializer(user)
        return Response({"message": "Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({"message": "Successfully", "data": serializer.data})
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data = request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "Successfully",
            "data": serializer.data
        })

    
