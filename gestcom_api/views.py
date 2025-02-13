from rest_framework import generics, status, viewsets
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.decorators import action
from .models import CustomUser, Role
from .serializers import CustomUserSerializer
from django.core.validators import EmailValidator, RegexValidator
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated
from .models import Boutique, Produit, Fournisseur, Facture, Client, FactureItem, Paiement, Model, Reapprovisionnement, Categorie, ReapItem
from .serializers import BoutiqueSerializer,ProduitSerializer,FournisseurSerializer,FactureSerializer,FactureItemSerializer,PaiementSerializer, CustomUserSerializer, ReapprovisionnementSerializer, CategorieSerializer, ReapItemSerializer
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# Constantes
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']

class UserViewSet(viewsets.ModelViewSet):
    """Gestion des utilisateurs : Inscription, Connexion, Profil et Mise à jour"""
    queryset = CustomUser.objects.all()  # ✅ Add this line
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Inscription d'un utilisateur",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['lastname', 'firstname', 'email', 'tel', 'password', 'confirmation'],
            properties={
                'lastname': openapi.Schema(type=openapi.TYPE_STRING),
                'firstname': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                'tel': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format="password"),
                'confirmation': openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={201: "Utilisateur créé avec succès"}
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Inscription d'un utilisateur"""
        lastname = request.data.get('lastname')
        firstname = request.data.get('firstname')
        email = request.data.get('email')
        tel = request.data.get('tel')
        password = request.data.get('password')
        confirmation = request.data.get('confirmation')

        # Validation des champs requis
        if not all([lastname, firstname, email, tel, password, confirmation]):
            return Response({'error': 'Veuillez fournir tous les champs requis'}, status=status.HTTP_400_BAD_REQUEST)

        # Validation du mot de passe
        try:
            self.validate_password(password)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirmation:
            return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        # Validation du téléphone
        phone_regex = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Le numéro doit être au format: '+999999999'"
        )
        try:
            phone_regex(tel)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Validation de l'email
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            return Response({'error': 'Format d\'email invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Un compte avec cet email existe déjà'}, status=status.HTTP_400_BAD_REQUEST)

        # Création de l'utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname
        )

        role, _ = Role.objects.get_or_create(libelleRole="admin")
        custom_user = CustomUser .objects.create(user=user, tel=tel, role=role)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'user': CustomUserSerializer(custom_user).data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Connexion d'un utilisateur",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={200: "Connexion réussie"}
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Connexion d'un utilisateur"""
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Veuillez fournir un email et un mot de passe'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification du rate limiting
        cache_key = f"login_attempts_{email}"
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            return Response({'error': 'Trop de tentatives de connexion. Veuillez réessayer dans 5 minutes.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        user = authenticate(username=email, password=password)
        if not user:
            # Incrémentation du compteur d'échecs
            cache.set(cache_key, attempts + 1, LOGIN_TIMEOUT)
            return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

        # Réinitialisation du compteur en cas de succès
        cache.delete(cache_key)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'user_id': user.id, 'email': user.email}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Mise à jour du profil utilisateur",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'lastname': openapi.Schema(type=openapi.TYPE_STRING),
                'firstname': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format="password"),
                'photo': openapi.Schema(type=openapi.TYPE_FILE),
            },
        ),
        responses={200: "Profil mis à jour avec succès"}
    )
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Mise à jour des informations de l'utilisateur"""
        user = request.user
        custom_user = user.customuser

        lastname = request.data.get('lastname', user.last_name)
        firstname = request.data.get('firstname', user.first_name)
        email = request.data.get('email', user.email)
        password = request.data.get('password')
        photo = request.FILES.get('photo')

        # Validation de l'email si modifié
        if email != user.email:
            email_validator = EmailValidator()
            try:
                email_validator(email)
                if User.objects.filter(email=email).exists():
                    return Response({'error': 'Cet email est déjà utilisé par un autre compte.'}, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError:
                return Response({'error': 'Format d\'email invalide'}, status=status.HTTP_400_BAD_REQUEST)

        # Validation et mise à jour de la photo
        if photo:
            try:
                self.validate_image(photo)
                custom_user.photo = photo
                custom_user.save()
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Mise à jour des informations utilisateur
        user.last_name = lastname
        user.first_name = firstname
        user.email = email

        if password:
            try:
                self.validate_password(password)
                user.set_password(password)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.save()

        return Response({'message': 'Informations mises à jour avec succès.'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Réinitialisation du mot de passe - Demande",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format="email"),
            },
        ),
        responses={200: "Code de réinitialisation envoyé"}
    )
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Réinitialisation du mot de passe"""
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Veuillez fournir une adresse e-mail.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'message': 'Si un compte existe avec cet email, un lien de réinitialisation sera envoyé.'}, status=status.HTTP_200_OK)

        # Génération du token de réinitialisation
        reset_token = self.generate_reset_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        # Envoi de l'email
        send_mail(
            subject='Réinitialisation de votre mot de passe',
            message=f'Bonjour {user.first_name},\n\n'
                   f'Pour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant :\n'
                   f'{reset_link}\n\n'
                   f'Ce lien est valable pendant 24 heures.\n\n'
                   f'Si vous n\'avez pas demandé cette réinitialisation, ignorez cet email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Si un compte existe avec cet email, un lien de réinitialisation sera envoyé.'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Confirmer la réinitialisation du mot de passe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', 'new_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={200: "Mot de passe réinitialisé avec succès"}
    )
    @action(detail=False, methods=['post'])
    def confirm_reset_password(self, request):
        """Confirmer la réinitialisation du mot de passe"""
        token = request.data.get('token')
        new_password = request.data.get('password')

        if not token or not new_password:
            return Response({'error': 'Token et nouveau mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Décodage et validation du token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])

            # Validation du nouveau mot de passe
            self.validate_password(new_password)

            # Mise à jour du mot de passe
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Mot de passe réinitialisé avec succès.'}, status=status.HTTP_200_OK)

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return Response({'error': 'Lien de réinitialisation invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Récupérer le profil utilisateur",
        responses={200: CustomUserSerializer()}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Affichage des informations du profil utilisateur"""
        return Response({
            'lastname': request.user.last_name,
            'firstname': request.user.first_name,
            'email': request.user.email,
            'photo': request.user.customuser.photo.url if request.user.customuser.photo else None,
            'role': request.user.customuser.role.libelleRole
        })

    def validate_password(self, password):
        """Validation complexe du mot de passe"""
        if len(password) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre")
        if not any(char.isupper() for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins une majuscule")
        if not any(char.islower() for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins une minuscule")
        if not any(char in "!@#$%^&*(),.?\":{}|<>" for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial")

    def validate_image(self, image):
        """Validation de l'image"""
        if image.size > MAX_FILE_SIZE:
            raise ValidationError("L'image ne doit pas dépasser 5MB")
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Format d'image non supporté")

    def generate_reset_token(self, user):
        """Génère un token JWT pour la réinitialisation du mot de passe"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'token_type': 'password_reset'
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# Gestion des boutiques
class BoutiqueViewSet(viewsets.ModelViewSet):
    """CRUD des boutiques"""
    serializer_class = BoutiqueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Récupérer uniquement les boutiques de l'utilisateur connecté"""
        return Boutique.objects.filter(manager=self.request.user.customuser)

    def perform_create(self, serializer):
        """Création d'une boutique"""
        serializer.save(manager=self.request.user.customuser)

    @swagger_auto_schema(
        operation_description="Mise à jour d'une boutique",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nom_shop': openapi.Schema(type=openapi.TYPE_STRING),
                'adresse_shop': openapi.Schema(type=openapi.TYPE_STRING),
                'descript_shop': openapi.Schema(type=openapi.TYPE_STRING),
                'logo': openapi.Schema(type=openapi.TYPE_FILE),
            },
        ),
        responses={200: "Boutique mise à jour avec succès"}
    )
    @action(detail=True, methods=['put'])
    def update_boutique(self, request, pk=None):
        """Mise à jour d'une boutique"""
        boutique = self.get_object()

        nom = request.data.get('nom_shop', boutique.nom_shop)
        adresse = request.data.get('adresse_shop', boutique.adresse_shop)
        description = request.data.get('descript_shop', boutique.descript_shop)
        logo = request.FILES.get('logo', boutique.logo)

        if Boutique.objects.exclude(id=boutique.id).filter(nom_shop=nom).exists():
            return Response({'error': 'Une autre boutique utilise déjà ce nom.'}, status=status.HTTP_400_BAD_REQUEST)

        boutique.nom_shop = nom
        boutique.adresse_shop = adresse
        boutique.descript_shop = description
        if logo:
            boutique.logo = logo
        boutique.save()

        return Response({'message': 'Boutique mise à jour avec succès.', 'boutique': BoutiqueSerializer(boutique).data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Suppression d'une boutique",
        responses={200: "Boutique supprimée avec succès"}
    )
    @action(detail=True, methods=['delete'])
    def delete_boutique(self, request, pk=None):
        """Suppression d'une boutique"""
        boutique = self.get_object()
        boutique.delete()
        return Response({'message': 'Boutique supprimée avec succès.'}, status=status.HTTP_200_OK)

    
    
class ProduitViewSet(viewsets.ModelViewSet):
    """CRUD des produits"""
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrer les produits par boutique si un `boutique_id` est fourni"""
        boutique_id = self.request.query_params.get('boutique_id')
        if boutique_id:
            return Produit.objects.filter(boutique_id=boutique_id)
        return Produit.objects.all()  # Retourne tous les produits si aucun filtre

    def perform_create(self, serializer):
        """Création d'un produit"""
        # Ensure the product is associated with the user's boutique
        boutique_id = self.request.data.get('boutique_id')
        try:
            boutique = Boutique.objects.get(id=boutique_id, manager=self.request.user.customuser)
            serializer.save(boutique=boutique)
        except Boutique.DoesNotExist:
            raise Response({'error': 'La boutique spécifiée n\'existe pas ou vous n\'y avez pas accès.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Mise à jour d'un produit",
        request_body=ProduitSerializer,
        responses={200: "Produit mis à jour avec succès"}
    )
    @action(detail=True, methods=['put'])
    def update_produit(self, request, pk=None):
        """Mise à jour d'un produit"""
        produit = self.get_object()
        
        # Ensure the product belongs to the user's boutique
        if produit.boutique.manager != self.request.user.customuser:
            return Response({'error': 'Vous n\'êtes pas autorisé à modifier ce produit.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProduitSerializer(produit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Produit mis à jour avec succès.', 'produit': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Suppression d'un produit",
        responses={200: "Produit supprimé avec succès"}
    )
    @action(detail=True, methods=['delete'])
    def delete_produit(self, request, pk=None):
        """Suppression d'un produit"""
        produit = self.get_object()
        
        # Ensure the product belongs to the user's boutique
        if produit.boutique.manager != self.request.user.customuser:
            return Response({'error': 'Vous n\'êtes pas autorisé à supprimer ce produit.'}, status=status.HTTP_403_FORBIDDEN)

        produit.delete()
        return Response({'message': 'Produit supprimé avec succès.'}, status=status.HTTP_200_OK)

class FournisseurViewSet(viewsets.ModelViewSet):
    """CRUD des fournisseurs"""
    serializer_class = FournisseurSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Récupérer les fournisseurs associés à la boutique de l'utilisateur connecté"""
        boutique_id = self.request.query_params.get('boutique_id')
        if boutique_id:
            return Fournisseur.objects.filter(boutique_id=boutique_id)
        return Fournisseur.objects.none()  # Return an empty queryset if no boutique_id is provided

    def perform_create(self, serializer):
        """Création d'un fournisseur"""
        boutique_id = self.request.data.get('boutique_id')
        try:
            boutique = Boutique.objects.get(id=boutique_id, manager=self.request.user.customuser)
            serializer.save(boutique=boutique)
        except Boutique.DoesNotExist:
            return Response({'error': 'La boutique spécifiée n\'existe pas ou vous n\'y avez pas accès.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Mise à jour d'un fournisseur",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nom_fournisseur': openapi.Schema(type=openapi.TYPE_STRING),
                'adresse_fournisseur': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_fournisseur': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: "Fournisseur mis à jour avec succès"}
    )
    @action(detail=True, methods=['put'])
    def update_fournisseur(self, request, pk=None):
        """Mise à jour d'un fournisseur"""
        fournisseur = self.get_object()
        
        # Ensure the fournisseur belongs to the user's boutique
        if fournisseur.boutique.manager != self.request.user.customuser:
            return Response({'error': 'Vous n\'êtes pas autorisé à modifier ce fournisseur.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = FournisseurSerializer(fournisseur, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Fournisseur mis à jour avec succès.', 'fournisseur': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Suppression d'un fournisseur",
        responses={200: "Fournisseur supprimé avec succès"}
    )
    @action(detail=True, methods=['delete'])
    def delete_fournisseur(self, request, pk=None):
        """Suppression d'un fournisseur"""
        fournisseur = self.get_object()
        
        # Ensure the fournisseur belongs to the user's boutique
        if fournisseur.boutique.manager != self.request.user.customuser:
            return Response({'error': 'Vous n\'êtes pas autorisé à supprimer ce fournisseur.'}, status=status.HTTP_403_FORBIDDEN)

        fournisseur.delete()
        return Response({'message': 'Fournisseur supprimé avec succès.'}, status=status.HTTP_200_OK)
    
class FactureViewSet(viewsets.ModelViewSet):
    """CRUD des factures"""
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Récupérer les factures associées à la boutique de l'utilisateur connecté"""
        boutique_id = self.request.query_params.get('boutique_id')
        if boutique_id:
            return Facture.objects.filter(boutique_id=boutique_id)
        return Facture.objects.none()  # Return an empty queryset if no boutique_id is provided

    def perform_create(self, serializer):
        """Création d'une facture"""
        boutique_id = self.request.data.get('boutique_id')
        client_id = self.request.data.get('client_id')
        
        try:
            boutique = Boutique.objects.get(id=boutique_id, manager=self.request.user.customuser)
            client = Client.objects.get(id=client_id)  # Assuming the client exists and is valid
            serializer.save(boutique=boutique, client=client)
        except Boutique.DoesNotExist:
            return Response({'error': 'La boutique spécifiée n\'existe pas ou vous n\'y avez pas accès.'}, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({'error': 'Le client spécifié n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Mise à jour d'une facture",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'total': openapi.Schema(type=openapi.TYPE_NUMBER, description="Total de la facture"),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="Statut de la facture"),
                'date_emission': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="Date d'émission"),
            },
        ),
        responses={200: "Facture mise à jour avec succès", 400: "Erreur de validation"}
    )
    @action(detail=True, methods=['put'])
    def update_facture(self, request, pk=None):
        """Mise à jour d'une facture"""
        facture = self.get_object()
        
        # Ensure the facture belongs to the user's boutique
        if facture.boutique.manager != self.request.user.customuser:
            return Response({'error': 'Vous n\'êtes pas autorisé à modifier cette facture.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = FactureSerializer(facture, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Facture mise à jour avec succès.', 'facture': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Suppression d'une facture",
        responses={200: "Facture supprimée avec succès", 403: "Non autorisé"}
    )
    @action(detail=True, methods=['delete'])
    def delete_facture(self, request, pk=None):
        """Suppression d'une facture"""
        facture = self.get_object()
        
        # Ensure the facture belongs to the user's boutique
        if facture.boutique.manager != self.request.user.customuser:
            return Response({'error': 'Vous n\'êtes pas autorisé à supprimer cette facture.'}, status=status.HTTP_403_FORBIDDEN)

        facture.delete()
        return Response({'message': 'Facture supprimée avec succès.'}, status=status.HTTP_200_OK)
    
class FactureItemViewSet(viewsets.ModelViewSet):
    """CRUD des items de facture"""
    serializer_class = FactureItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Récupérer les items de facture associés à une facture spécifique"""
        facture_id = self.request.query_params.get('facture_id')
        if facture_id:
            return FactureItem.objects.filter(facture_id=facture_id)
        return FactureItem.objects.none()  # Return an empty queryset if no facture_id is provided

    @swagger_auto_schema(
        operation_description="Création d'un item de facture",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['facture_id', 'produit_id', 'quantite', 'prix_unitaire'],
            properties={
                'facture_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID de la facture"),
                'produit_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du produit"),
                'quantite': openapi.Schema(type=openapi.TYPE_INTEGER, description="Quantité du produit"),
                'prix_unitaire': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Prix unitaire"),
            },
        ),
        responses={
            201: "Item de facture créé avec succès",
            400: "La facture spécifiée n'existe pas"
        }
    )
    def perform_create(self, serializer):
        """Création d'un item de facture"""
        facture_id = self.request.data.get('facture_id')
        try:
            facture = Facture.objects.get(id=facture_id)
            serializer.save(facture=facture)
        except Facture.DoesNotExist:
            return Response({'error': 'La facture spécifiée n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Mise à jour d'un item de facture",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quantite': openapi.Schema(type=openapi.TYPE_INTEGER, description="Nouvelle quantité"),
                'prix_unitaire': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Nouveau prix unitaire"),
            },
        ),
        responses={
            200: "Item de facture mis à jour avec succès",
            400: "Erreur de validation"
        }
    )
    @action(detail=True, methods=['put'])
    def update_facture_item(self, request, pk=None):
        """Mise à jour d'un item de facture"""
        facture_item = self.get_object()
        
        serializer = FactureItemSerializer(facture_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Item de facture mis à jour avec succès.', 'facture_item': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Suppression d'un item de facture",
        responses={
            200: "Item de facture supprimé avec succès"
        }
    )
    @action(detail=True, methods=['delete'])
    def delete_facture_item(self, request, pk=None):
        """Suppression d'un item de facture"""
        facture_item = self.get_object()
        facture_item.delete()
        return Response({'message': 'Item de facture supprimé avec succès.'}, status=status.HTTP_200_OK)
    
class PaiementViewSet(viewsets.ModelViewSet):
    """CRUD des paiements"""
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Récupérer les paiements associés à une facture spécifique"""
        facture_id = self.request.query_params.get('facture_id')
        if facture_id:
            return Paiement.objects.filter(facture_id=facture_id)
        return Paiement.objects.none()  # Return an empty queryset if no facture_id is provided

    @swagger_auto_schema(
        operation_description="Création d'un paiement",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['facture_id', 'mode_paie_id', 'montant'],
            properties={
                'facture_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID de la facture"),
                'mode_paie_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du mode de paiement"),
                'montant': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Montant du paiement"),
            },
        ),
        responses={
            201: "Paiement créé avec succès",
            400: "La facture ou le mode de paiement spécifié n'existe pas"
        }
    )
    def perform_create(self, serializer):
        """Création d'un paiement"""
        facture_id = self.request.data.get('facture_id')
        mode_paie_id = self.request.data.get('mode_paie_id')
        
        try:
            facture = Facture.objects.get(id=facture_id)
            mode_paie = Model.objects.get(id=mode_paie_id)
            serializer.save(facture=facture, mode_paie=mode_paie)
        except Facture.DoesNotExist:
            return Response({'error': 'La facture spécifiée n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)
        except Model.DoesNotExist:
            return Response({'error': 'Le mode de paiement spécifié n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Mise à jour d'un paiement",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'montant': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Nouveau montant"),
            },
        ),
        responses={
            200: "Paiement mis à jour avec succès",
            400: "Erreur de validation"
        }
    )
    @action(detail=True, methods=['put'])
    def update_paiement(self, request, pk=None):
        """Mise à jour d'un paiement"""
        paiement = self.get_object()
        
        serializer = PaiementSerializer(paiement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Paiement mis à jour avec succès.', 'paiement': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Suppression d'un paiement",
        responses={
            200: "Paiement supprimé avec succès"
        }
    )
    @action(detail=True, methods=['delete'])
    def delete_paiement(self, request, pk=None):
        """Suppression d'un paiement"""
        paiement = self.get_object()
        paiement.delete()
        return Response({'message': 'Paiement supprimé avec succès.'}, status=status.HTTP_200_OK)

class ReapprovisionnementViewSet(viewsets.ModelViewSet):
    """CRUD des réapprovisionnements"""
    serializer_class = ReapprovisionnementSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lister tous les réapprovisionnements d'une boutique ou ceux d’un fournisseur spécifique",
        manual_parameters=[
            openapi.Parameter(
                'boutique', openapi.IN_QUERY,
                description="ID de la boutique pour filtrer les réapprovisionnements",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'fournisseur', openapi.IN_QUERY,
                description="ID du fournisseur pour filtrer les réapprovisionnements",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: ReapprovisionnementSerializer(many=True)}
    )
    def get_queryset(self):
        """Lister tous les réapprovisionnements d'une boutique ou ceux d’un fournisseur spécifique"""
        boutique_id = self.request.query_params.get('boutique', None)
        fournisseur_id = self.request.query_params.get('fournisseur', None)

        queryset = Reapprovisionnement.objects.all()

        if boutique_id:
            queryset = queryset.filter(boutique_id=boutique_id)

        if fournisseur_id:
            queryset = queryset.filter(fournisseur_id=fournisseur_id)

        return queryset

    @swagger_auto_schema(
        operation_description="Créer un réapprovisionnement",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['fournisseur', 'boutique', 'num_reap'],
            properties={
                'fournisseur': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du fournisseur"),
                'boutique': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID de la boutique"),
                'num_reap': openapi.Schema(type=openapi.TYPE_STRING, description="Numéro unique du réapprovisionnement"),
            }
        ),
        responses={
            201: "Réapprovisionnement créé avec succès",
            400: "Erreur de validation (fournisseur introuvable, boutique introuvable, numéro déjà utilisé)"
        }
    )
    def perform_create(self, serializer):
        """Créer un réapprovisionnement"""
        fournisseur_id = self.request.data.get('fournisseur')
        boutique_id = self.request.data.get('boutique')

        if not fournisseur_id or not boutique_id:
            raise ValidationError("Les champs 'fournisseur' et 'boutique' sont obligatoires.")

        if Reapprovisionnement.objects.filter(num_reap=self.request.data.get('num_reap')).exists():
            raise ValidationError("Un réapprovisionnement avec ce numéro existe déjà.")

        try:
            fournisseur = Fournisseur.objects.get(id=fournisseur_id)
        except Fournisseur.DoesNotExist:
            raise ValidationError("Fournisseur introuvable.")

        try:
            boutique = Boutique.objects.get(id=boutique_id)
        except Boutique.DoesNotExist:
            raise ValidationError("Boutique introuvable.")

        serializer.save(fournisseur=fournisseur, boutique=boutique)

    @swagger_auto_schema(
        operation_description="Modifier un réapprovisionnement",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'num_reap': openapi.Schema(type=openapi.TYPE_STRING, description="Nouveau numéro unique du réapprovisionnement"),
            }
        ),
        responses={
            200: "Réapprovisionnement mis à jour avec succès",
            400: "Erreur de validation (numéro déjà utilisé)"
        }
    )
    def perform_update(self, serializer):
        """Modifier un réapprovisionnement"""
        instance = self.get_object()
        num_reap = self.request.data.get('num_reap', instance.num_reap)

        if num_reap != instance.num_reap and Reapprovisionnement.objects.filter(num_reap=num_reap).exists():
            raise ValidationError("Ce numéro de réapprovisionnement est déjà utilisé.")

        serializer.save()

class CategorieViewSet(viewsets.ModelViewSet):
    """CRUD des catégories"""
    serializer_class = CategorieSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lister toutes les catégories",
        responses={200: CategorieSerializer(many=True)}
    )
    def get_queryset(self):
        """Lister toutes les catégories"""
        return Categorie.objects.all()

    @swagger_auto_schema(
        operation_description="Créer une catégorie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['libelle_categorie'],
            properties={
                'libelle_categorie': openapi.Schema(type=openapi.TYPE_STRING, description="Libellé unique de la catégorie"),
            }
        ),
        responses={
            201: "Catégorie créée avec succès",
            400: "Erreur de validation (libellé déjà utilisé)"
        }
    )
    def perform_create(self, serializer):
        """Créer une catégorie"""
        libelle_categorie = self.request.data.get('libelle_categorie')

        if Categorie.objects.filter(libelle_categorie=libelle_categorie).exists():
            raise ValidationError("Une catégorie avec ce libellé existe déjà.")

        serializer.save()

    @swagger_auto_schema(
        operation_description="Modifier une catégorie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'libelle_categorie': openapi.Schema(type=openapi.TYPE_STRING, description="Nouveau libellé unique de la catégorie"),
            }
        ),
        responses={
            200: "Catégorie mise à jour avec succès",
            400: "Erreur de validation (libellé déjà utilisé)"
        }
    )
    def perform_update(self, serializer):
        """Modifier une catégorie"""
        instance = self.get_object()
        libelle_categorie = self.request.data.get('libelle_categorie', instance.libelle_categorie)

        if libelle_categorie != instance.libelle_categorie and Categorie.objects.filter(libelle_categorie=libelle_categorie).exists():
            raise ValidationError("Ce libellé de catégorie est déjà utilisé.")

        serializer.save()

class ReapItemViewSet(viewsets.ModelViewSet):
    """CRUD des items de réapprovisionnement"""
    serializer_class = ReapItemSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lister tous les items de réapprovisionnement ou ceux d’un réapprovisionnement spécifique.",
        manual_parameters=[
            openapi.Parameter(
                'reappro',
                openapi.IN_QUERY,
                description="ID du réapprovisionnement pour filtrer les items",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: ReapItemSerializer(many=True)}
    )
    def get_queryset(self):
        """Lister tous les items de réapprovisionnement ou ceux d’un réapprovisionnement spécifique"""
        reappro_id = self.request.query_params.get('reappro', None)
        if reappro_id:
            return ReapItem.objects.filter(reappro_id=reappro_id)
        return ReapItem.objects.all()

    @swagger_auto_schema(
        operation_description="Créer un item de réapprovisionnement",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['reappro', 'produit'],
            properties={
                'reappro': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du réapprovisionnement"),
                'produit': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du produit"),
            }
        ),
        responses={
            201: "Item de réapprovisionnement créé avec succès",
            400: "Erreur de validation (réapprovisionnement ou produit introuvable)"
        }
    )
    def perform_create(self, serializer):
        """Créer un item de réapprovisionnement"""
        reappro_id = self.request.data.get('reappro')
        produit_id = self.request.data.get('produit')

        if not reappro_id or not produit_id:
            raise ValidationError("Les champs 'reappro' et 'produit' sont obligatoires.")

        try:
            reappro = Reapprovisionnement.objects.get(id=reappro_id)
        except Reapprovisionnement.DoesNotExist:
            raise ValidationError("Réapprovisionnement introuvable.")

        try:
            produit = Produit.objects.get(id=produit_id)
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable.")

        serializer.save(reappro=reappro, produit=produit)

    @swagger_auto_schema(
        operation_description="Modifier un item de réapprovisionnement",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'produit': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du nouveau produit"),
            }
        ),
        responses={
            200: "Item de réapprovisionnement mis à jour avec succès",
            400: "Erreur de validation (produit introuvable)"
        }
    )
    def perform_update(self, serializer):
        """Modifier un item de réapprovisionnement"""
        instance = self.get_object()
        produit_id = self.request.data.get('produit', instance.produit.id)

        try:
            produit = Produit.objects.get(id=produit_id)
        except Produit.DoesNotExist:
            raise ValidationError("Produit introuvable.")

        serializer.save(produit=produit)