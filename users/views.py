from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from .models import User
from .serializers import UserSerializer, MyTokenObtainPairSerializer

# API Đăng ký User
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Gán nhóm mặc định (nếu không truyền group thì mặc định là "User")
        group_name = request.data.get("group", "User")  
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        user.save()

        return Response({"message": "User registered successfully!", "user": serializer.data})

# API Đăng nhập
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise AuthenticationFailed("Email and password are required!")

        user = User.objects.filter(email=email).first()
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
            return Response({'detail': 'Refresh token is required'}, status=400)
        try:
            if refresh_token.startswith("Bearer "):
                refresh_token = refresh_token[7:]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'detail': 'Successfully logged out.'}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)