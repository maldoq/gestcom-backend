from rest_framework import generics, status, viewsets
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.decorators import action
from .models import CustomUser, Role
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated
from .models import Boutique, Produit, Fournisseur, Facture, Client, FactureItem, Paiement, Model
from .serializers import BoutiqueSerializer,ProduitSerializer,FournisseurSerializer,FactureSerializer,FactureItemSerializer,PaiementSerializer


# Gestion des utilisateurs
class UserViewSet(viewsets.ViewSet):
    """Gestion des utilisateurs : Inscription, Connexion, Profil et Mise à jour"""

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Inscription d'un utilisateur"""
        lastname = request.data.get('lastname')
        firstname = request.data.get('firstname')
        email = request.data.get('email')
        tel = request.data.get('tel')
        password = request.data.get('password')
        confirmation = request.data.get('confirmation')

        if not all([lastname, firstname, email, tel, password, confirmation]):
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

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Connexion d'un utilisateur"""
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Veuillez fournir un email et un mot de passe'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if not user:
            return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'email': user.email}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Mise à jour des informations de l'utilisateur"""
        user = request.user
        custom_user = user.customuser

        user.last_name = request.data.get('lastname', user.last_name)
        user.email = request.data.get('email', user.email)
        password = request.data.get('password', None)
        photo = request.data.get('photo', custom_user.photo)

        if password:
            user.set_password(password)

        user.save()

        if photo:
            custom_user.photo = photo
            custom_user.save()

        return Response({'message': 'Informations mises à jour avec succès.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Réinitialisation du mot de passe"""
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({'error': 'Aucun compte trouvé avec cet email.'}, status=status.HTTP_404_NOT_FOUND)

        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()

        send_mail(
            subject='Réinitialisation de votre mot de passe',
            message=f'Bonjour {user.first_name},\n\nVotre nouveau mot de passe est : {new_password}\n\nVeuillez le modifier après connexion.',
            from_email='support@monapp.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Un e-mail avec un nouveau mot de passe a été envoyé.'}, status=status.HTTP_200_OK)

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

    def perform_create(self, serializer):
        """Création d'un item de facture"""
        facture_id = self.request.data.get('facture_id')
        try:
            facture = Facture.objects.get(id=facture_id)
            serializer.save(facture=facture)
        except Facture.DoesNotExist:
            return Response({'error': 'La facture spécifiée n\'existe pas.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_facture_item(self, request, pk=None):
        """Mise à jour d'un item de facture"""
        facture_item = self.get_object()
        
        serializer = FactureItemSerializer(facture_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Item de facture mis à jour avec succès.', 'facture_item': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=True, methods=['put'])
    def update_paiement(self, request, pk=None):
        """Mise à jour d'un paiement"""
        paiement = self.get_object()
        
        serializer = PaiementSerializer(paiement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Paiement mis à jour avec succès.', 'paiement': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_paiement(self, request, pk=None):
        """Suppression d'un paiement"""
        paiement = self.get_object()
        paiement.delete()
        return Response({'message': 'Paiement supprimé avec succès.'}, status=status.HTTP_200_OK)