from rest_framework import serializers
from .models import CustomUser, Role
from django.contrib.auth.models import User
from .models import Boutique

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

class BoutiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boutique
        fields = '__all__'