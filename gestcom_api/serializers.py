from rest_framework import serializers
from .models import CustomUser, Role
from django.contrib.auth.models import User
from .models import Boutique, Produit, CustomUser, Role, Fournisseur, Facture, FactureItem, Paiement, Reapprovisionnement

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    role = RoleSerializer()

    class Meta:
        model = CustomUser
        fields = '__all__'

class BoutiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boutique
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'  # Inclut tous les champs du modèle Produit

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'  # Include all fields from the Fournisseur model

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'  # Include all fields from the Facture model

class FactureItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactureItem
        fields = '__all__'  # Include all fields from the FactureItem model

class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = '__all__'  # Include all fields from the Paiement model

class ReapprovisionnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reapprovisionnement
        fields = '__all__'