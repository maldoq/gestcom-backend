from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.validators import RegexValidator, EmailValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
import jwt
from .models import CustomUser, Role, Boutique, Client
from .serializers import CustomUserSerializer, BoutiqueSerializer, ClientSerializer
from .models import Fournisseur
from .models import Reapprovisionnement, Fournisseur
from .serializers import ReapprovisionnementSerializer


# Constantes
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()

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

    def post(self, request, *args, **kwargs):
        lastname = request.data.get('lastname')
        firstname = request.data.get('firstname')
        email = request.data.get('email')
        tel = request.data.get('tel')
        password = request.data.get('password')
        confirmation = request.data.get('confirmation')

        # Validation des champs requis
        if not all([lastname, firstname, email, tel, password, confirmation]):
            return Response({
                'error': 'Veuillez fournir tous les champs requis'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validation du mot de passe
        try:
            self.validate_password(password)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirmation:
            return Response({
                'error': 'Les mots de passe ne correspondent pas'
            }, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({
                'error': 'Format d\'email invalide'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Un compte avec cet email existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Création de l'utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname
        )

        role, _ = Role.objects.get_or_create(libelleRole="instaff")
        custom_user = CustomUser.objects.create(user=user, tel=tel, role=role)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': CustomUserSerializer(custom_user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': 'Veuillez fournir un email et un mot de passe'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Vérification du rate limiting
        cache_key = f"login_attempts_{email}"
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            return Response({
                'error': 'Trop de tentatives de connexion. Veuillez réessayer dans 5 minutes.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        user = authenticate(username=email, password=password)
        if not user:
            # Incrémentation du compteur d'échecs
            cache.set(cache_key, attempts + 1, LOGIN_TIMEOUT)
            return Response({
                'error': 'Identifiants incorrects'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Réinitialisation du compteur en cas de succès
        cache.delete(cache_key)
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def validate_image(self, image):
        if image.size > MAX_FILE_SIZE:
            raise ValidationError("L'image ne doit pas dépasser 5MB")
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Format d'image non supporté")

    def put(self, request):
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
                    return Response({
                        'error': 'Cet email est déjà utilisé par un autre compte.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError:
                return Response({
                    'error': 'Format d\'email invalide'
                }, status=status.HTTP_400_BAD_REQUEST)

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
                RegisterView().validate_password(password)
                user.set_password(password)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.save()

        return Response({
            'message': 'Informations mises à jour avec succès.'
        }, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def generate_reset_token(self, user):
        """Génère un token JWT pour la réinitialisation du mot de passe"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'token_type': 'password_reset'
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'error': 'Veuillez fournir une adresse e-mail.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            # Réponse volontairement vague pour la sécurité
            return Response({
                'message': 'Si un compte existe avec cet email, un lien de réinitialisation sera envoyé.'
            }, status=status.HTTP_200_OK)

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

        return Response({
            'message': 'Si un compte existe avec cet email, un lien de réinitialisation sera envoyé.'
        }, status=status.HTTP_200_OK)

class ConfirmResetPasswordView(APIView):
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('password')
        
        if not token or not new_password:
            return Response({
                'error': 'Token et nouveau mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Décodage et validation du token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])

            # Validation du nouveau mot de passe
            RegisterView().validate_password(new_password)
            
            # Mise à jour du mot de passe
            user.set_password(new_password)
            user.save()

            return Response({
                'message': 'Mot de passe réinitialisé avec succès.'
            }, status=status.HTTP_200_OK)

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return Response({
                'error': 'Lien de réinitialisation invalide ou expiré'
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'error': 'Utilisateur introuvable'
            }, status=status.HTTP_404_NOT_FOUND)

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

class BoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def validate_image(self, image):
        if image.size > MAX_FILE_SIZE:
            raise ValidationError("Le logo ne doit pas dépasser 5MB")
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Format de logo non supporté")

    def post(self, request):
        """Créer une boutique"""
        nom = request.data.get('nom')
        adresse = request.data.get('adresse')
        description = request.data.get('description')
        logo = request.FILES.get('logo')

        if not nom or not adresse:
            return Response({
                'error': 'Le nom et l\'adresse sont obligatoires.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Boutique.objects.filter(nom=nom).exists():
            return Response({
                'error': 'Une boutique avec ce nom existe déjà.'
            }, status=status.HTTP_400_BAD_REQUEST)

        boutique = Boutique(
            nom=nom,
            adresse=adresse,
            description=description,
            proprietaire=request.user
        )

        if logo:
            try:
                self.validate_image(logo)
                boutique.logo = logo
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        boutique.save()

        return Response({
            'message': 'Boutique créée avec succès.',
            'boutique': BoutiqueSerializer(boutique).data
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Lister toutes les boutiques de l'utilisateur"""
        boutiques = Boutique.objects.filter(proprietaire=request.user)
        serializer = BoutiqueSerializer(boutiques, many=True)
        return Response({'boutiques': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, boutique_id):
        """Modifier une boutique"""
        try:
            boutique = Boutique.objects.get(id=boutique_id, proprietaire=request.user)
        except Boutique.DoesNotExist:
            return Response({
                'error': 'Boutique introuvable ou accès non autorisé.'
            }, status=status.HTTP_404_NOT_FOUND)

        nom = request.data.get('nom', boutique.nom)
        adresse = request.data.get('adresse', boutique.adresse)
        description = request.data.get('description', boutique.description)
        logo = request.FILES.get('logo')

        if nom != boutique.nom and Boutique.objects.filter(nom=nom).exists():
            return Response({
                'error': 'Une autre boutique utilise déjà ce nom.'
            }, status=status.HTTP_400_BAD_REQUEST)

        boutique.nom = nom
        boutique.a

class ReapprovisionnementView(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ Créer un réapprovisionnement
    def post(self, request):
        numReap = request.data.get('numReap')
        dateReap = request.data.get('dateReap')
        quantiteReap = request.data.get('quantiteReap')
        prixReap = request.data.get('prixReap')
        fournisseur_id = request.data.get('fournisseur')

        if not (numReap and dateReap and quantiteReap and prixReap and fournisseur_id):
            return Response({'error': 'Veuillez remplir tous les champs obligatoires.'}, status=status.HTTP_400_BAD_REQUEST)

        if Reapprovisionnement.objects.filter(numReap=numReap).exists():
            return Response({'error': 'Un réapprovisionnement avec ce numéro existe déjà.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fournisseur = Fournisseur.objects.get(id=fournisseur_id)
        except Fournisseur.DoesNotExist:
            return Response({'error': 'Fournisseur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        reapprovisionnement = Reapprovisionnement.objects.create(
            numReap=numReap,
            dateReap=dateReap,
            quantiteReap=quantiteReap,
            prixReap=prixReap,
            fournisseur=fournisseur
        )

        return Response({'message': 'Réapprovisionnement créé avec succès.', 'reapprovisionnement': ReapprovisionnementSerializer(reapprovisionnement).data}, status=status.HTTP_201_CREATED)

    # ✅ Lister tous les réapprovisionnements ou ceux d’un fournisseur spécifique
    def get(self, request):
        fournisseur_id = request.query_params.get('fournisseur', None)
        if fournisseur_id:
            reapprovisionnements = Reapprovisionnement.objects.filter(fournisseur_id=fournisseur_id)
        else:
            reapprovisionnements = Reapprovisionnement.objects.all()

        return Response({'reapprovisionnements': ReapprovisionnementSerializer(reapprovisionnements, many=True).data}, status=status.HTTP_200_OK)

    # ✅ Modifier un réapprovisionnement
    def put(self, request, idReap):
        try:
            reapprovisionnement = Reapprovisionnement.objects.get(idReap=idReap)
        except Reapprovisionnement.DoesNotExist:
            return Response({'error': 'Réapprovisionnement introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        numReap = request.data.get('numReap', reapprovisionnement.numReap)
        dateReap = request.data.get('dateReap', reapprovisionnement.dateReap)
        quantiteReap = request.data.get('quantiteReap', reapprovisionnement.quantiteReap)
        prixReap = request.data.get('prixReap', reapprovisionnement.prixReap)
        status = request.data.get('status', reapprovisionnement.status)

        if numReap != reapprovisionnement.numReap and Reapprovisionnement.objects.filter(numReap=numReap).exists():
            return Response({'error': 'Ce numéro de réapprovisionnement est déjà utilisé.'}, status=status.HTTP_400_BAD_REQUEST)

        reapprovisionnement.numReap = numReap
        reapprovisionnement.dateReap = dateReap
        reapprovisionnement.quantiteReap = quantiteReap
        reapprovisionnement.prixReap = prixReap
        reapprovisionnement.status = status
        reapprovisionnement.save()

        return Response({'message': 'Réapprovisionnement mis à jour avec succès.', 'reapprovisionnement': ReapprovisionnementSerializer(reapprovisionnement).data}, status=status.HTTP_200_OK)

    # ✅ Supprimer un réapprovisionnement
    def delete(self, request, idReap):
        try:
            reapprovisionnement = Reapprovisionnement.objects.get(idReap=idReap)
        except Reapprovisionnement.DoesNotExist:
            return Response({'error': 'Réapprovisionnement introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        reapprovisionnement.delete()
        return Response({'message': 'Réapprovisionnement supprimé avec succès.'}, status=status.HTTP_200_OK)