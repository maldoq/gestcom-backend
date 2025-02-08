from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BoutiqueViewSet, ProduitViewSet, FournisseurViewSet, FactureViewSet, FactureItemViewSet, PaiementViewSet, ReapprovisionnementViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'boutiques', BoutiqueViewSet, basename='boutiques')
router.register(r'fournisseurs', FournisseurViewSet, basename='fournisseur')
router.register(r'factures', FactureViewSet, basename='facture')
router.register(r'facture-items', FactureItemViewSet, basename='facture-item')
router.register(r'paiements', PaiementViewSet, basename='paiement')
router.register(r'reapprovisionnements', ReapprovisionnementViewSet, basename='reapprovisionnement')

urlpatterns = [
    path('', include(router.urls)),
]