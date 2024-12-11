from .models import HonourBoard
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed


class HonourBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HonourBoard
        fields = '__all__'

    def validate(self, data):
        """
        Perform validation on ending_date and joining_date together.
        """
        joining_date = data.get('joining_date')
        ending_date = data.get('ending_date')

        if ending_date and joining_date and ending_date <= joining_date:
            raise serializers.ValidationError({
                "ending_date": "Ending date must be after the joining date."
            })

        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)
    class Meta:
        model=get_user_model()
        fields=('username','profile_picture','email','password','confirm_password')

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password doesn't match")
        return data

    def create(self,validated_data):
        validated_data.pop('confirm_password')
        User=get_user_model()

        user=User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
        )
        if 'profile_picture' in validated_data:
            user.profile_picture = validated_data['profile_picture']
        # user.role=validated_data['role']
        user.is_approved=False
        user.save()
        return user

class StaffApproveSerializer(serializers.ModelSerializer):    
    class Meta:
        model=get_user_model()
        fields=('username','email','is_approved','role')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Check if the user is approved
        if not user.is_approved:
            raise AuthenticationFailed("Your account has not been approved yet.")

        return data