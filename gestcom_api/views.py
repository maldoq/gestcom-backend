from rest_framework import generics
from .models import Categorie, Produit, Fournisseur, Magasin, Stock, Commande, LigneCommande
from .serializers import CategorieSerializer, ProduitSerializer, FournisseurSerializer, MagasinSerializer, StockSerializer, CommandeSerializer, LigneCommandeSerializer

# CRUD pour Role
class RoleListCreate(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

# CRUD pour Utilisateur
class CustomUserListCreate(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CustomUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

# CRUD pour Type
class TypeListCreate(generics.ListCreateAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

class TypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

# CRUD pour Boutique
class BoutiqueListCreate(generics.ListCreateAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer

class BoutiqueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer

class CategorieListCreate(generics.ListCreateAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer


from django.urls import path


urlpatterns = [
    # Routes pour Client
    path('clients/', ClientListCreate.as_view(), name='client-list-create'),
    path('clients/<str:pk>/', ClientDetail.as_view(), name='client-detail'),

    # Routes pour Référence
    path('references/', ReferenceListCreate.as_view(), name='reference-list-create'),
    path('references/<str:pk>/', ReferenceDetail.as_view(), name='reference-detail'),

    # Routes pour Réception
    path('receptions/', ReceptionListCreate.as_view(), name='reception-list-create'),
    path('receptions/<str:pk>/', ReceptionDetail.as_view(), name='reception-detail'),

    # Routes pour Facture
    path('factures/', FactureListCreate.as_view(), name='facture-list-create'),
    path('factures/<str:pk>/', FactureDetail.as_view(), name='facture-detail'),

    # Routes pour Facturation
    path('facturations/', FacturationListCreate.as_view(), name='facturation-list-create'),
    path('facturations/<str:pk>/', FacturationDetail.as_view(), name='facturation-detail'),

    # Routes pour Achat
    path('achats/', AchatListCreate.as_view(), name='achat-list-create'),
    path('achats/<str:pk>/', AchatDetail.as_view(), name='achat-detail'),
]
