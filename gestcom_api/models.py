from django.db import models
from django.contrib.auth.models import User

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

# Client
class Client(models.Model):
    nomClient = models.CharField(max_length=50,null=False)
    emailClient = models.EmailField(unique=True,null=False)
    telClient = models.CharField(max_length=20, unique=True)
    adresseClient = models.TextField(null=True, blank=True)
    boutique = models.ForeignKey(Boutique,on_delete=models.CASCADE,null=False)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nomClient} {self.emailClient}"

# Catégorie
class Categorie(models.Model):
    libelle_categorie = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle_categorie

# Produit
class Produit(models.Model):
    idProduit = models.CharField(max_length=50,primary_key=True,null=False,unique=True)
    libelleProduit = models.CharField(max_length=100, unique=True)
    descriptProduit = models.TextField(null=True, blank=True)
    marqueProduit = models.CharField(max_length=30, null=True)
    prixProduit = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    stockProduit = models.IntegerField(default=0)
    seuilProduit = models.SmallIntegerField(null=False,default=0)
    image = models.ImageField(upload_to='produits/', null=True, blank=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, null=True)
    boutique = models.ForeignKey(Boutique,on_delete=models.PROTECT,null=False)


    def __str__(self):
        return self.libelle_produit

# Fournisseur
class Fournisseur(models.Model):
    nomFournisseur = models.CharField(max_length=100, unique=True)
    contactFournisseur = models.CharField(max_length=20, null=True, blank=True, unique=True)
    emailFournisseur = models.EmailField(null=True, blank=True, unique=True)
    adresseFournisseur = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nomFournisseur

class Facture(models.Model):
    idFact = models.CharField(primary_key=True,null=False,unique=True,max_length=50)
    numFact = models.CharField(max_length=100, null=True)
    prixHTFact = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    tvaFact = models.DecimalField(max_digits=3, decimal_places=2,null=True)
    reducFact = models.DecimalField(max_digits=3, decimal_places=2,null=True)
    statePaieFact = models.CharField(max_length=20,null=True)
    dateEchFact = models.DateField(null=True)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)

    def __str__(self):
        return self.numFact
    
class FactureItem(models.Model):
    quantiteFactI = models.SmallIntegerField(null=False)
    prixFactI = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.produit.libelleProduit} - {self.facture.numFact}"
    
class Model(models.Model):
    libelleMod = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.libelleMod}"

class Paiement(models.Model):
    numPaie = models.CharField(max_length=50)
    datePaie = models.DateField(null=True)
    montantPaie = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    refTransPaie = models.CharField(max_length=50)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    modePaie = models.ForeignKey(Model, on_delete=models.CASCADE)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numPaie} - {self.facture.numFact}"


class Reapprovisionnement(models.Model):
    numReap = models.CharField(max_length=50)
    dateReap = models.DateField(null=True)
    quantiteReap = models.SmallIntegerField(null=False)
    prixReap = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    status = models.BooleanField(default=True,null=False)
    dateAjout = models.DateTimeField(auto_now_add=True)
    dateModif = models.DateTimeField(auto_now=True)

class ReapItem(models.Model):
    quantiteReapI = models.SmallIntegerField(null=False)
    prixReap = models.DecimalField(max_digits=15, decimal_places=2,null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    reappro = models.ForeignKey(Reapprovisionnement, on_delete=models.CASCADE)