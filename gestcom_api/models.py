from django.db import models
from django.contrib.auth.models import User

# Partie Utilisateur
class Role(models.Model):
    libelle_role = models.CharField(max_length=50,null=False)
    descript_role = models.TextField(null=True)

    def __str__(self):
        return self.libelle_role

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    indicateur_user = models.CharField(max_length=5,default='+225',null=True)
    tel_user = models.CharField(max_length=10,null=False)

    def __str__(self):
        return f'{self.user.email} - {self.role.libelle_role}'

# Partie Boutique
class Type(models.Model):
    libelle_type = models.CharField(max_length=50,null=False)
    descript_type = models.TextField(null=True)
    status = models.BooleanField(default=True,null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_type


class Boutique(models.Model):
    nom_shop = models.CharField(max_length=50,null=False)
    descript_shop = models.TextField(null=True)
    adresse_shop = models.CharField(max_length=100,null=True)
    status = models.BooleanField(default=True,null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    types = models.ForeignKey(Type, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nom_shop

# Client
class Client(models.Model):
    nom_client = models.CharField(max_length=50,null=False)
    email_client = models.EmailField(unique=True,null=False)
    tel_client = models.CharField(max_length=20, unique=True)
    adresse_client = models.TextField(null=True, blank=True)
    boutique = models.ForeignKey(Boutique,on_delete=models.CASCADE,null=False)
    status = models.BooleanField(default=True,null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom_client} {self.email_client}"

# Catégorie
class Categorie(models.Model):
    libelle_categorie = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=True,null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_categorie

# Produit
class Produit(models.Model):
    id_produit = models.CharField(max_length=50,primary_key=True,null=False,unique=True)
    libelle_produit = models.CharField(max_length=100, unique=True)
    descript_produit = models.TextField(null=True, blank=True)
    marque_produit = models.CharField(max_length=30, null=True)
    prix_produit = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    stock_produit = models.IntegerField(default=0)
    seuil_produit = models.SmallIntegerField(null=False,default=0)
    image = models.ImageField(upload_to='produits/', null=True, blank=True)
    status = models.BooleanField(default=True,null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, null=True)
    boutique = models.ForeignKey(Boutique,on_delete=models.PROTECT,null=False)


    def __str__(self):
        return self.libelle_produit

# Fournisseur
class Fournisseur(models.Model):
    nom_fournisseur = models.CharField(max_length=100, unique=True)
    contact_fournisseur = models.CharField(max_length=20, null=True, blank=True, unique=True)
    email_fournisseur = models.EmailField(null=True, blank=True, unique=True)
    adresse_fournisseur = models.TextField(null=True, blank=True)
    boutique = models.ForeignKey(Boutique,on_delete=models.CASCADE,null=False)
    status = models.BooleanField(default=True,null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom_fournisseur

class Facture(models.Model):
    id_fact = models.CharField(primary_key=True,null=False,unique=True,max_length=50)
    num_fact = models.CharField(max_length=100, null=True)
    prixHT_fact = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    tva_fact = models.DecimalField(max_digits=3, decimal_places=2,null=True)
    reduc_fact = models.DecimalField(max_digits=3, decimal_places=2,null=True)
    statePaie_fact = models.CharField(max_length=20,null=True)
    dateEch_fact = models.DateField(null=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    boutique = models.ForeignKey(Boutique,on_delete=models.PROTECT,null=False)

    def __str__(self):
        return self.num_fact
    
class FactureItem(models.Model):
    quantite_factI = models.SmallIntegerField(null=False)
    prix_factI = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.produit.libelle_produit} - {self.facture.num_fact}"
    
class Model(models.Model):
    libelle_mod = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.libelle_mod}"

class Paiement(models.Model):
    num_paie = models.CharField(max_length=50)
    date_paie = models.DateField(null=True)
    montant_paie = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    refTrans_paie = models.CharField(max_length=50)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    mode_paie = models.ForeignKey(Model, on_delete=models.CASCADE)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.num_paie} - {self.facture.num_fact}"


class Reapprovisionnement(models.Model):
    num_reap = models.CharField(max_length=50)
    date_reap = models.DateField(null=True)
    quantite_reap = models.SmallIntegerField(null=False)
    prix_reap = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

class ReapItem(models.Model):
    quantite_reapI = models.SmallIntegerField(null=False)
    prix_reapI = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    reappro = models.ForeignKey(Reapprovisionnement, on_delete=models.CASCADE)
