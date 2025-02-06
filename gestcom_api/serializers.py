from rest_framework import serializers
from .models import CustomUser, Role
from django.contrib.auth.models import User

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    role = RoleSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'user', 'telUser', 'role']
