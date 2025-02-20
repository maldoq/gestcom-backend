from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BoutiqueViewSet, ProduitViewSet, FournisseurViewSet, FactureViewSet, FactureItemViewSet, PaiementViewSet, ReapprovisionnementViewSet, CategorieViewSet, ReapItemViewSet, TypeViewSet, ClientViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'boutiques', BoutiqueViewSet, basename='boutiques')
router.register(r'fournisseurs', FournisseurViewSet, basename='fournisseur')
router.register(r'factures', FactureViewSet, basename='facture')
router.register(r'facture-items', FactureItemViewSet, basename='facture-item')
router.register(r'paiements', PaiementViewSet, basename='paiement')
router.register(r'reapprovisionnements', ReapprovisionnementViewSet, basename='reapprovisionnement')
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'reap-items', ReapItemViewSet, basename='reapitem')
router.register(r'types', TypeViewSet, basename='type')
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]