from django.contrib import admin
from .models import Role, Utilisateur, Type, Boutique, Client, Categorie, Produit, Fournisseur, Magasin, Stock, Achat, DetailAchat

admin.site.register(Role)
admin.site.register(Utilisateur)
admin.site.register(Type)
admin.site.register(Boutique)
admin.site.register(Client)
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(Fournisseur)
admin.site.register(Magasin)
admin.site.register(Stock)
admin.site.register(Achat)
admin.site.register(DetailAchat)
