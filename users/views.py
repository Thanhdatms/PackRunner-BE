from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from .models import User, Address
from django.conf import settings
from .serializers import UserSerializer, MyTokenObtainPairSerializer, AddressSerializer
from .permissions import *
from .otpverify import sendSmSOTP
from drf_spectacular.utils import extend_schema
from api_doc.schemas.auth_schemas import login_schema, register_schema, verify_opt_schema, logout_schema
from utils.response import success_response, fail_response
from rest_framework.permissions import AllowAny

# Register API

@extend_schema(tags=['Auth'])
@register_schema
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
@extend_schema(tags=['Auth'])
@login_schema
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            raise fail_response("Phone number and password are required!")

        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise fail_response("User not found!")
        
        if not user.check_password(password):
            raise fail_response("Incorrect password!")
        # Generate OTP
        user.generate_otp()
        phone_number = "84" + user.phone_number[1:]
        otp = user.otp

        # try:
        #     sendSmSOTP(phone_number=phone_number, otp=otp)
        # except Exception as e:
        #     return fail_response("Failed to send OTP. Please try again later.", status_code=500)

        return success_response(message="OTP sent. Please verify to complete login.", data={
            "phone_number": phone_number, 
        })

@extend_schema(tags=['Auth'])
@verify_opt_schema
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

@extend_schema(tags=['Auth'])
@logout_schema
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        access_token = request.META.get('HTTP_AUTHORIZATION')

        if not refresh_token:
            return Response({'message': 'Refresh token is required'}, status=400)

        try:
            # Strip prefix from refresh token
            if refresh_token.startswith("Bearer "):
                refresh_token = refresh_token[7:]

            # Blacklist refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Handle access token (optional)
            if access_token and access_token.startswith("Bearer "):
                raw_access = access_token[7:]
                try:
                    AccessToken(raw_access).blacklist()  # Will raise if unsupported
                except AttributeError:
                    # AccessToken does not support blacklisting
                    pass


            # Update user
            user = request.user
            user.otp_require = True
            user.save(update_fields=["otp_require"])

            return Response({'message': 'Successfully logged out.'}, status=200)

        except Exception as e:
            return Response({'detail': 'Invalid or expired token.'}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    tags=['User']
)    
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many = True)
        return Response({"message": "Successfully", "data": serializer.data })

@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    tags=['User']
)       
class UserDetailView(APIView):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = UserSerializer(user)
        return Response({"message": "Successfully", "data": serializer.data}, status=status.HTTP_200_OK)

@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    tags=['User']
)   
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

@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    tags=['Address']
)
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

@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    tags=['Address']
)
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
        