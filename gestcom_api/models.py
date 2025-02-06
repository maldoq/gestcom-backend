from django.db import models

# Role
class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    libelle_role = models.CharField(max_length=50, unique=True)
    descript_role = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.libelle_role

    class Meta:
        ordering = ["libelle_role"]
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"

# Utilisateur
class Utilisateur(models.Model):
    id_user = models.AutoField(primary_key=True)
    nom_user = models.CharField(max_length=100)
    prenom_user = models.CharField(max_length=100)
    email_user = models.EmailField(unique=True)
    tel_user = models.CharField(max_length=20, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.nom_user} {self.prenom_user}"

    class Meta:
        ordering = ["nom_user", "prenom_user"]
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

# Type de boutique
class Type(models.Model):
    id_type = models.AutoField(primary_key=True)
    libelle_type = models.CharField(max_length=100, unique=True)
    descript_type = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_type

# Boutique
class Boutique(models.Model):
    id_boutique = models.AutoField(primary_key=True)
    nom_shop = models.CharField(max_length=100, unique=True)
    descript_shop = models.TextField(null=True, blank=True)
    adresse_shop = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, null=True)
    type = models.ForeignKey(Type, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.nom_shop

# Client
class Client(models.Model):
    id_client = models.AutoField(primary_key=True)
    nom_client = models.CharField(max_length=100)
    prenom_client = models.CharField(max_length=100)
    email_client = models.EmailField(unique=True)
    telephone_client = models.CharField(max_length=20, unique=True)
    adresse_client = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom_client} {self.prenom_client}"

# Catégorie
class Categorie(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    libelle_categorie = models.CharField(max_length=100, unique=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_categorie

# Produit
class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    libelle_produit = models.CharField(max_length=100, unique=True)
    description_produit = models.TextField(null=True, blank=True)
    prix_produit = models.DecimalField(max_digits=10, decimal_places=2)
    stock_produit = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, null=True)
    fournisseurs = models.ManyToManyField('Fournisseur', related_name="produits")

    def __str__(self):
        return self.libelle_produit

# Fournisseur
class Fournisseur(models.Model):
    id_fournisseur = models.AutoField(primary_key=True)
    libelle_fournisseur = models.CharField(max_length=100, unique=True)
    contact_fournisseur = models.CharField(max_length=20, null=True, blank=True, unique=True)
    email_fournisseur = models.EmailField(null=True, blank=True, unique=True)
    adresse_fournisseur = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.libelle_fournisseur

# Magasin
class Magasin(models.Model):
    id_magasin = models.AutoField(primary_key=True)
    libelle_magasin = models.CharField(max_length=100, unique=True)
    adresse_magasin = models.TextField(null=True, blank=True)
    telephone_magasin = models.CharField(max_length=20, null=True, blank=True, unique=True)

    def __str__(self):
        return self.libelle_magasin

# Stock
class Stock(models.Model):
    id_stock = models.AutoField(primary_key=True)
    quantite = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.produit.libelle_produit} - {self.magasin.libelle_magasin} ({self.quantite})"

# Achat
class Achat(models.Model):
    id_achat = models.AutoField(primary_key=True)
    date_achat = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"Achat {self.id_achat} - {self.client.nom_client}"

# Détail Achat (Gestion des produits achetés)
class DetailAchat(models.Model):
    id_detail = models.AutoField(primary_key=True)
    achat = models.ForeignKey(Achat, on_delete=models.CASCADE, related_name="details")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.achat.id_achat} - {self.produit.libelle_produit} ({self.quantite})"

    class Meta:
        unique_together = ('achat', 'produit')
