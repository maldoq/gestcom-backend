from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Partie Utilisateur
class Role(models.Model):
    libelleRole = models.CharField(max_length=50,null=False)
    descriptRole = models.TextField(null=True)

    def __str__(self):
        return self.libelleRole

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    indicateurUser = models.CharField(max_length=5,default='+225',null=True)
    telUser = models.CharField(max_length=10,null=False)

    def __str__(self):
        return f'{self.user.email} - {self.role.libelleRole}'

# Partie Boutique
class Type(models.Model):
    libelleType = models.CharField(max_length=50,null=False)
    descriptType = models.TextField(null=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelleType


class Boutique(models.Model):
    nomShop = models.CharField(max_length=50,null=False)
    descriptShop = models.TextField(null=True)
    adresseShop = models.CharField(max_length=100,null=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    types = models.ForeignKey(Type, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nomShop

# Catégorie de produits
class Categorie(models.Model):
    id_categorie = models.CharField(max_length=255, primary_key=True)
    libelle_categorie = models.CharField(max_length=100)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_categorie

# Produit
class Produit(models.Model):
    id_produit = models.CharField(max_length=255, primary_key=True)
    libelle_produit = models.CharField(max_length=100)
    description_produit = models.TextField(null=True, blank=True)
    prix_produit = models.DecimalField(max_digits=10, decimal_places=2)
    stock_produit = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name="produits")

    def __str__(self):
        return self.libelle_produit

# Fournisseur
class Fournisseur(models.Model):
    id_fournisseur = models.CharField(max_length=255, primary_key=True)
    libelle_fournisseur = models.CharField(max_length=100)
    contact_fournisseur = models.CharField(max_length=20, null=True, blank=True)
    email_fournisseur = models.EmailField(null=True, blank=True)
    adresse_fournisseur = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.libelle_fournisseur

# Magasin
class Magasin(models.Model):
    id_magasin = models.CharField(max_length=255, primary_key=True)
    libelle_magasin = models.CharField(max_length=100)
    adresse_magasin = models.TextField(null=True, blank=True)
    telephone_magasin = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.libelle_magasin

# Stock
class Stock(models.Model):
    id_stock = models.CharField(max_length=255, primary_key=True)
    quantite = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="stocks")
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name="stocks")

    def __str__(self):
        return f"{self.produit.libelle_produit} - {self.magasin.libelle_magasin} ({self.quantite})"

# Commande
class Commande(models.Model):
    id_commande = models.CharField(max_length=255, primary_key=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE, related_name="commandes")  # Client doit être défini

    def __str__(self):
        return f"Commande {self.id_commande} - {self.client}"

# LigneCommande (Relation Commande - Produit)
class LigneCommande(models.Model):
    id_ligne_commande = models.CharField(max_length=255, primary_key=True)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes_commande")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="lignes_commande")

    def __str__(self):
        return f"{self.commande.id_commande} - {self.produit.libelle_produit} ({self.quantite})"
