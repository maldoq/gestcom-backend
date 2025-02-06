from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import CustomUser, Role
from .serializers import CustomUserSerializer, RoleSerializer
from rest_framework.permissions import IsAuthenticated

# Inscription Utilisateur (Nom, Prénom, Email, Téléphone, Mot de passe, Confirmation) avec rôle "instaff"
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        lastname = request.data.get('lastname')
        firstname = request.data.get('firstname')
        email = request.data.get('email')
        tel = request.data.get('tel')
        password = request.data.get('password')
        confirmation = request.data.get('confirmation')

        # Vérification des champs obligatoires
        if not (lastname and firstname and email and tel and password and confirmation):
            return Response({'error': 'Veuillez fournir tous les champs requis'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification de la correspondance des mots de passe
        if password != confirmation:
            return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification de l'unicité de l'email
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Un compte avec cet email existe déjà'}, status=status.HTTP_400_BAD_REQUEST)

        # Création de l'utilisateur
        user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)

        # Attribution automatique du rôle "instaff"
        role, _ = Role.objects.get_or_create(name="instaff")  # Vérifie si le rôle "instaff" existe, sinon le crée
        custom_user = CustomUser.objects.create(user=user, tel=tel, role=role)

        # Génération du token
        token, _ = Token.objects.get_or_create(user=user)

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
