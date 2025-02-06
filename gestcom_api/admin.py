from django.contrib import admin
from .models import Role, Type, Boutique, Client, Categorie, Produit, Fournisseur, CustomUser, Reapprovisionnement, ReapItem, Paiement, Model, Facture, FactureItem

admin.site.register(Role)
admin.site.register(CustomUser)
admin.site.register(Type)
admin.site.register(Boutique)
admin.site.register(Client)
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(Fournisseur)
admin.site.register(Reapprovisionnement)
admin.site.register(ReapItem)
admin.site.register(Paiement)
admin.site.register(Model)
admin.site.register(Facture)
admin.site.register(FactureItem)
