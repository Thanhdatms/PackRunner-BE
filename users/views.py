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
from .serializers import UserSerializer, MyTokenObtainPairSerializer, AddressSerializer, FaceRegisterSerializer
from .permissions import *
from .otpverify import sendSmSOTP
from drf_spectacular.utils import extend_schema
from api_doc.schemas.auth_schemas import login_schema, register_schema, verify_opt_schema, logout_schema
from utils.response import success_response, fail_response
from rest_framework.permissions import AllowAny
from api_doc.schemas.user_schemas import user_profile_schema, address_schema, address_detail_schema, face_register_schema
from rest_framework import serializers
from utils.response import fail_response, success_response
from rest_framework.parsers import MultiPartParser, FormParser

# Register API

@extend_schema(tags=['Auth'])
@register_schema
class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            group_name = request.data.get("group", "User")  
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            # return Response({
            #     "message": "User registered successfully!", 
            #     "data": serializer.data
            # })
            return success_response(message="User registered successfully!", data=serializer.data)
        
        except Exception as e:
            return fail_response(str(e), status_code=400)

# Login API
@extend_schema(tags=['Auth'])
@login_schema
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            phone_number = request.data.get("phone_number")
            password = request.data.get("password")

            if not phone_number or not password:
                return fail_response("Phone number and password are required!")

            user = User.objects.filter(phone_number=phone_number).first()
            if user is None:
                return fail_response("User not found!")
            
            if not user.check_password(password):
                return fail_response("Incorrect password!")
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
        except Exception as e:
            return fail_response(str(e), status_code=400)

@extend_schema(tags=['Auth'])
@verify_opt_schema
class VerifyOTPView(APIView):
    def patch(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return fail_response("User not found", status_code=404)

        if user.otp_max_out and now() < user.otp_max_out:
            return fail_response("Account is locked for 1 hour after max attempts.", status_code=403)

        if now() > user.otp_expiry:
            return fail_response("OTP has expired. Please request a new one.", status_code=400)

        # Check OTP validity
        if user.otp != otp:
            user.max_otp_try -= 1

            if user.max_otp_try < 1:
                # Lock user for 1 hour if max attempts are exceeded
                user.otp_max_out = now() + timedelta(hours=1)
            user.save()
            return fail_response("Incorrect OTP. Please try again.", status_code=400)

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
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many = True)
            return Response({"message": "Successfully", "data": serializer.data })
        except Exception as e:
            return fail_response(str(e), status_code=400)
@extend_schema(
    request=UserSerializer,
    responses=UserSerializer,
    tags=['User']
)       
class UserDetailView(APIView):
    def get(self, request, id):
        try:
            user = get_object_or_404(User, id=id)
            serializer = UserSerializer(user)
            return Response({"message": "Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return fail_response(str(e), status_code=400)

@extend_schema(tags=['User']) 
@user_profile_schema  
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response({"message": "Successfully", "data": serializer.data})
        except Exception as e:
            return fail_response(str(e), status_code=400)
        
    def put(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user, data = request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return Response({
                "message": "Successfully",
                "data": serializer.data
            })
        except Exception as e:
            return fail_response(str(e), status_code=400)

@extend_schema(tags=['Address'])
@address_schema
class AddressView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request):
        try:
            serializer = AddressSerializer(data = request.data, context = {'request': request})

            if serializer.is_valid(raise_exception=True):
                serializer.save(user = request.user)
                return Response({
                    "message": "Successfully",
                    "data": serializer.data
                })
        except Exception as e:
            return fail_response(str(e), status_code=400)

    def get(self, request):
        try:
            user = request.user

            addresses = Address.objects.filter(user = user)
            serializer = AddressSerializer(addresses, many = True)

            return Response({
                    "message": "Successfully",
                    "data": serializer.data
                })
        except Exception as e:
            return fail_response(str(e), status_code=400)
    
@extend_schema(tags=['Address'])
@address_detail_schema
class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, pk):
        try:
            user = request.user 
            address = Address.objects.filter(user=user, id=pk).first()
            
            if address:
                address.delete()
                return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return fail_response(str(e), status_code=400)
            
    def patch(self, request, pk):
        try:
            user = request.user
            address = Address.objects.filter(user=user, id=pk).first()

            if not address:
                return fail_response("Address not found", status_code=404)

            serializer = AddressSerializer(address, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return success_response(message="Address updated successfully", data=serializer.data)
        except Exception as e:
            return fail_response(str(e), status_code=400)

@extend_schema(tags=['RegisterFace'])
@face_register_schema
class RegisterFaceView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = FaceRegisterSerializer
    
    def post(self, request):
        try:
            user = request.user
            face_file = request.FILES.get('face_file')

            if not face_file:
                return fail_response("No face file provided", status_code=400)
            # delete old face_url if exists
            if user.face_url:
                user.face_url.delete(save=False)
            
            user.face_url = face_file
            user.save()
            face_url = request.build_absolute_uri(user.face_url.url)
            
            return success_response(message="Face URL registered successfully", data={"face_url": face_url})
        except Exception as e:
            return fail_response(str(e), status_code=400)
        
    def get(self, request):
        try:
            user = request.user
            if user.face_url:
                face_url = request.build_absolute_uri(user.face_url.url)
                return success_response(message="Face URL retrieved successfully", data={"face_url": face_url})
            else:
                return fail_response("No face URL found", status_code=404)
        except Exception as e:
            return fail_response(str(e), status_code=400)