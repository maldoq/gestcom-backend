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