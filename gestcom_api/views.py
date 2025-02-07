from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from .models import CustomUser, Role
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated
from .models import Boutique
from .serializers import BoutiqueSerializer


# Inscription Utilisateur avec rôle "instaff"
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        lastname = request.data.get('lastname')
        firstname = request.data.get('firstname')
        email = request.data.get('email')
        tel = request.data.get('tel')
        password = request.data.get('password')
        confirmation = request.data.get('confirmation')

        if not (lastname and firstname and email and tel and password and confirmation):
            return Response({'error': 'Veuillez fournir tous les champs requis'}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirmation:
            return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Un compte avec cet email existe déjà'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)

        role, _ = Role.objects.get_or_create(libelleRole="instaff")
        custom_user = CustomUser.objects.create(user=user, tel=tel, role=role)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'user': CustomUserSerializer(custom_user).data}, status=status.HTTP_201_CREATED)

# Connexion Utilisateur
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Veuillez fournir un email et un mot de passe'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if not user:
            return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'email': user.email}, status=status.HTTP_200_OK)

# Modification des informations personnelles
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        custom_user = user.customuser

        # Récupérer les données envoyées
        lastname = request.data.get('lastname', user.last_name)
        email = request.data.get('email', user.email)
        password = request.data.get('password', None)
        photo = request.data.get('photo', custom_user.photo)

        # Vérification de l'unicité de l'email si modifié
        if email != user.email and User.objects.filter(email=email).exists():
            return Response({'error': 'Cet email est déjà utilisé par un autre compte.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mise à jour des informations
        user.last_name = lastname
        user.email = email

        if password:
            user.set_password(password)

        user.save()

        # Mise à jour de la photo si fournie
        if photo:
            custom_user.photo = photo
            custom_user.save()

        return Response({'message': 'Informations mises à jour avec succès.'}, status=status.HTTP_200_OK)

# Réinitialisation du mot de passe par e-mail
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Veuillez fournir une adresse e-mail.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({'error': 'Aucun compte trouvé avec cet email.'}, status=status.HTTP_404_NOT_FOUND)

        # Génération d'un nouveau mot de passe temporaire
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()

        # Envoi de l'e-mail
        send_mail(
            subject='Réinitialisation de votre mot de passe',
            message=f'Bonjour {user.first_name},\n\nVotre nouveau mot de passe est : {new_password}\n\nVeuillez le modifier après connexion.',
            from_email='support@monapp.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Un e-mail avec un nouveau mot de passe a été envoyé.'}, status=status.HTTP_200_OK)

# Vue Profil Utilisateur
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'lastname': request.user.last_name,
            'firstname': request.user.first_name,
            'email': request.user.email,
            'photo': request.user.customuser.photo.url if request.user.customuser.photo else None,
            'role': request.user.customuser.role.libelleRole
        })

# Créer une boutique
class CreateBoutiqueView(generics.CreateAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        nom = request.data.get('nom')
        adresse = request.data.get('adresse')
        description = request.data.get('description', None)

        if not nom or not adresse:
            return Response({'error': 'Le nom et l\'adresse sont obligatoires.'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si le nom de la boutique est déjà pris
        if Boutique.objects.filter(nom=nom).exists():
            return Response({'error': 'Une boutique avec ce nom existe déjà.'}, status=status.HTTP_400_BAD_REQUEST)

        boutique = Boutique.objects.create(
            nom=nom,
            adresse=adresse,
            description=description,
            proprietaire=request.user
        )

        return Response({'message': 'Boutique créée avec succès.', 'boutique': BoutiqueSerializer(boutique).data}, status=status.HTTP_201_CREATED)

# Lister toutes les boutiques de l'administrateur
class ListBoutiquesView(generics.ListAPIView):
    serializer_class = BoutiqueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Boutique.objects.filter(proprietaire=self.request.user)

# Modifier une boutique
class UpdateBoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, boutique_id):
        try:
            boutique = Boutique.objects.get(id=boutique_id, proprietaire=request.user)
        except Boutique.DoesNotExist:
            return Response({'error': 'Boutique introuvable ou accès non autorisé.'}, status=status.HTTP_404_NOT_FOUND)

        nom = request.data.get('nom', boutique.nom)
        adresse = request.data.get('adresse', boutique.adresse)
        description = request.data.get('description', boutique.description)
        logo = request.FILES.get('logo', boutique.logo)

        # Vérifier si le nom est déjà utilisé par une autre boutique
        if Boutique.objects.exclude(id=boutique_id).filter(nom=nom).exists():
            return Response({'error': 'Une autre boutique utilise déjà ce nom.'}, status=status.HTTP_400_BAD_REQUEST)

        boutique.nom = nom
        boutique.adresse = adresse
        boutique.description = description
        if logo:
            boutique.logo = logo
        boutique.save()

        return Response({'message': 'Boutique mise à jour avec succès.', 'boutique': BoutiqueSerializer(boutique).data}, status=status.HTTP_200_OK)

# Supprimer une boutique
class DeleteBoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, boutique_id):
        try:
            boutique = Boutique.objects.get(id=boutique_id, proprietaire=request.user)
        except Boutique.DoesNotExist:
            return Response({'error': 'Boutique introuvable ou accès non autorisé.'}, status=status.HTTP_404_NOT_FOUND)

        boutique.delete()
        return Response({'message': 'Boutique supprimée avec succès.'}, status=status.HTTP_200_OK)

# Définir les modes de paiement acceptés
class UpdateModesPaiementView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, boutique_id):
        try:
            boutique = Boutique.objects.get(id=boutique_id, proprietaire=request.user)
        except Boutique.DoesNotExist:
            return Response({'error': 'Boutique introuvable ou accès non autorisé.'}, status=status.HTTP_404_NOT_FOUND)

        modes_paiement = request.data.get('modes_paiement')

        if not isinstance(modes_paiement, list) or not all(isinstance(mode, str) for mode in modes_paiement):
            return Response({'error': 'Veuillez fournir une liste valide des modes de paiement.'}, status=status.HTTP_400_BAD_REQUEST)

        boutique.modes_paiement = modes_paiement
        boutique.save()

        return Response({'message': 'Modes de paiement mis à jour avec succès.', 'boutique': BoutiqueSerializer(boutique).data}, status=status.HTTP_200_OK)