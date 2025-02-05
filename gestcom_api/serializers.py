from rest_framework import serializers
from .models import Categorie, Produit, Fournisseur, Magasin, Stock, Commande, LigneCommande

# Serializer pour Catégorie
class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'

# Serializer pour Produit
class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

# Serializer pour Fournisseur
class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'

# Serializer pour Magasin
class MagasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magasin
        fields = '__all__'

# Serializer pour Stock
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

# Serializer pour Commande
class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = '__all__'

# Serializer pour LigneCommande (relation Commande - Produit)
class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = '__all__'
