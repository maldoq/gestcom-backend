from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import CustomUser, Role
from .serializers import CustomUserSerializer, RoleSerializer
from rest_framework.permissions import IsAuthenticated

# User Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        tel_user = request.data.get('telUser')
        role_id = request.data.get('role')

        if not (username and password and email):
            return Response({'error': 'Please provide all required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        role = Role.objects.get(id=role_id) if role_id else None
        custom_user = CustomUser.objects.create(user=user, telUser=tel_user, role=role)

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': CustomUserSerializer(custom_user).data}, status=status.HTTP_201_CREATED)

# User Login
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Veuillez renseigner l\'email et le mot de passe'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'L\'email n\'existe pas'}, status=status.HTTP_401_UNAUTHORIZED)

        # Authenticate using username (since Django's default `authenticate` uses `username`)
        user = authenticate(username=user.username, password=password)
        if not user:
            return Response({'error': 'L\'utilisateur n\'existe pas, veuillez en renseigner un valide'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate or retrieve token
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username}, status=status.HTTP_200_OK)

# Protected View Example
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'username': request.user.username, 'email': request.user.email})
