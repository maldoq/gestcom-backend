from django.contrib import admin
from .models import Categorie, Produit, Fournisseur, Magasin, Stock, Commande, LigneCommande

admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(Fournisseur)
admin.site.register(Magasin)
admin.site.register(Stock)
admin.site.register(Commande)
admin.site.register(LigneCommande)
