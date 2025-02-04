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