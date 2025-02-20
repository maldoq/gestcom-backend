from rest_framework import serializers
from .models import CustomUser, Role
from django.contrib.auth.models import User
from .models import Boutique, Produit, CustomUser, Role, Fournisseur, Facture, FactureItem, Paiement, Reapprovisionnement, Categorie, ReapItem, Type, Client,Model


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'libelle_type', 'descript_type', 'date_ajout', 'date_modif']

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['libelle_categorie','date_ajout','date_modif']  # Include all fields from the Categorie model

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
    manager = CustomUserSerializer(read_only=True)
    types = TypeSerializer(read_only=True)
    # Allow setting IDs on create/update
    manager_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True, source="manager")
    types_id = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all(), write_only=True, source="types")
    class Meta:
        model = Boutique
        fields = ['id','nom_shop','descript_shop','adresse_shop','date_ajout','date_modif','manager','types', 'manager_id', 'types_id']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'nom_client', 'email_client', 'tel_client', 'adresse_client', 
            'boutique', 'date_ajout', 'date_modif'
        ]

class ProduitSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    boutique = BoutiqueSerializer(read_only=True)

    boutique_id = serializers.PrimaryKeyRelatedField(queryset=Boutique.objects.all(), write_only=True, source="boutique")
    categorie_id = serializers.PrimaryKeyRelatedField(queryset=Categorie.objects.all(), write_only=True, source="categorie")
    class Meta:
        model = Produit
        fields = ['id_produit','libelle_produit','descript_produit','marque_produit','prix_produit','stock_produit','seuil_produit','image','date_ajout','date_modif','categorie','boutique','boutique_id','categorie_id']  # Inclut tous les champs du modèle Produit

class FournisseurSerializer(serializers.ModelSerializer):
    boutique = BoutiqueSerializer(read_only=True)

    boutique_id = serializers.PrimaryKeyRelatedField(queryset=Boutique.objects.all(), write_only=True, source="boutique")
    class Meta:
        model = Fournisseur
        fields = ['nom_fournisseur','contact_fournisseur','email_fournisseur','adresse_fournisseur','date_ajout','date_modif','boutique','boutique_id']  # Include all fields from the Fournisseur model

class FactureSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    boutique = BoutiqueSerializer(read_only=True)

    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True, source="client")
    boutique_id = serializers.PrimaryKeyRelatedField(queryset=Boutique.objects.all(), write_only=True, source="boutique")
    class Meta:
        model = Facture
        fields = ['id_fact','num_fact','prixHT_fact','tva_fact','reduc_fact','statePaie_fact','dateEch_fact','date_ajout','date_modif','client','boutique','client_id','boutique_id']  # Include all fields from the Facture model

class FactureItemSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    facture = FactureSerializer(read_only=True)

    produit_id = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all(), write_only=True, source="produit")
    facture_id = serializers.PrimaryKeyRelatedField(queryset=Facture.objects.all(), write_only=True, source="facture")
    class Meta:
        model = FactureItem
        fields = ['quantite_factI','prix_factI','produit','facture','produit_id','facture_id']  # Include all fields from the FactureItem model

class PaiementSerializer(serializers.ModelSerializer):
    facture = FactureSerializer(read_only=True)

    facture_id = serializers.PrimaryKeyRelatedField(queryset=Facture.objects.all(), write_only=True, source="facture")
    mode_paie_id = serializers.PrimaryKeyRelatedField(queryset=Model.objects.all(), write_only=True, source="mode_paie")
    class Meta:
        model = Paiement
        fields = ['num_paie','date_paie','montant_paie','refTrans_paie','date_ajout','date_modif','facture','facture_id','mode_paie_id']  # Include all fields from the Paiement model

class ReapprovisionnementSerializer(serializers.ModelSerializer):
    fournisseur = FournisseurSerializer(read_only=True)
    boutique = BoutiqueSerializer(read_only=True)

    boutique_id = serializers.PrimaryKeyRelatedField(queryset=Boutique.objects.all(), write_only=True, source="boutique")
    fournisseur_id = serializers.PrimaryKeyRelatedField(queryset=Fournisseur.objects.all(), write_only=True, source="fournisseur")
    class Meta:
        model = Reapprovisionnement
        fields = ['num_reap','date_reap','quantite_reap','prix_reap','date_ajout','date_modif','fournisseur','boutique','boutique_id','fournisseur_id']

class ReapItemSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    reappro = ReapprovisionnementSerializer(read_only=True)

    produit_id = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all(), write_only=True, source="produit")
    reappro_id = serializers.PrimaryKeyRelatedField(queryset=Reapprovisionnement.objects.all(), write_only=True, source="reappro")
    class Meta:
        model = ReapItem
        fields = ['quantite_reapI','prix_reapI','produit','reappro','produit_id','reappro_id']  # Include all fields from the ReapItem model

