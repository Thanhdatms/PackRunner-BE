from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from .models import User, Address
from django.conf import settings
from .serializers import UserSerializer, MyTokenObtainPairSerializer, AddressSerializer
from .permissions import *
from .otpverify import sendSmSOTP

# Register API
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
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
        # Generate OTP
        user.generate_otp()
        phone_number = "84" + user.phone_number[1:]
        otp = user.otp

        sendSmSOTP(phone_number=phone_number, otp=otp)

        return Response({
            "message": "OTP sent. Please verify to complete login."
        })

class VerifyOTPView(APIView):
    def patch(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if user.otp_max_out and now() < user.otp_max_out:
            return Response({"error": "Too many failed attempts. Try again later."}, status=status.HTTP_403_FORBIDDEN)
        
        if now() > user.otp_expiry:
            return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP validity
        if user.otp != otp:
            user.max_otp_try -= 1

            if user.max_otp_try < 1:
                # Lock user for 1 hour if max attempts are exceeded
                user.otp_max_out = now() + timedelta(hours=1)
            user.save()
            return Response({"error": "Incorrect OTP. Account is locked for 1 hour after max attempts."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.otp == otp:
            user.is_active = True
            user.otp = None
            user.otp_max_out = None
            user.max_otp_try = settings.MAX_OTP_TRY  # Reset max attempts
            user.otp_expiry = None
            user.otp_require = False

            user.save()

            refresh = RefreshToken.for_user(user)
            token_data = MyTokenObtainPairSerializer.get_token(user)

            return Response({
                "message": "OTP verified successfully",
                "data":{
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "groups": token_data["groups"],
                    "permissions": token_data["permissions"]
                }
            }, status=status.HTTP_200_OK)

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

            user = request.user
            user.otp_require = True
            user.save(update_fields=["otp_require"])

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

class AddressView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        serializer = AddressSerializer(data = request.data, context = {'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save(user = request.user)
            return Response({
                "message": "Successfully",
                "data": serializer.data
            })

    def get(self, request):
        user = request.user

        addresses = Address.objects.filter(user = user)
        serializer = AddressSerializer(addresses, many = True)

        return Response({
                "message": "Successfully",
                "data": serializer.data
            })

class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, pk):
        user = request.user 
        address = Address.objects.filter(user=user, id=pk).first()
        
        if address:
            address.delete()
            return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        
