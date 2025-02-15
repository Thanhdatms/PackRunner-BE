from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

# Serializer User
class UserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=False, default=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'phone_number', 'is_active', 'is_banned', 'date_of_birth']
        extra_kwargs = {
            'password': {'write_only': True}  # Prevent password not show in response
        }

    def validate_email(self, value):
        if "gmail.com" not in value:
            raise serializers.ValidationError('Please correct your gmail!')
        return value
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data) # giai nen validated data
        if password:
            instance.set_password(password)  # encrypt password
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        groups = list(user.groups.values_list('name', flat=True))
        token["groups"] = groups

        permissions = list(user.get_all_permissions())
        token["permissions"] = permissions

        return token
