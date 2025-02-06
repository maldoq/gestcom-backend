from django.urls import path
from .views import RoleListCreate, RoleDetail, CustomUserListCreate, CustomUserDetail, TypeListCreate, TypeDetail, BoutiqueListCreate, BoutiqueDetail, CategorieListCreate
from .views import (
    ClientListCreate, ClientDetail,
    ReferenceListCreate, ReferenceDetail,
    ReceptionListCreate, ReceptionDetail,
    FactureListCreate, FactureDetail,
    FacturationListCreate, FacturationDetail,
    AchatListCreate, AchatDetail
)

urlpatterns = [
    path('roles/', RoleListCreate.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetail.as_view(), name='role-detail'),

    path('utilisateurs/', CustomUserListCreate.as_view(), name='utilisateur-list-create'),
    path('utilisateurs/<int:pk>/', CustomUserDetail.as_view(), name='utilisateur-detail'),

    path('types/', TypeListCreate.as_view(), name='type-list-create'),
    path('types/<int:pk>/', TypeDetail.as_view(), name='type-detail'),

    path('boutiques/', BoutiqueListCreate.as_view(), name='boutique-list-create'),
    path('boutiques/<int:pk>/', BoutiqueDetail.as_view(), name='boutique-detail'),

    path('categories/', CategorieListCreate.as_view(), name='categorie-list-create'),
    # Routes pour Client
    path('clients/', ClientListCreate.as_view(), name='client-list-create'),
    path('clients/<str:pk>/', ClientDetail.as_view(), name='client-detail'),

    # Routes pour Référence
    path('references/', ReferenceListCreate.as_view(), name='reference-list-create'),
    path('references/<str:pk>/', ReferenceDetail.as_view(), name='reference-detail'),

    # Routes pour Réception
    path('receptions/', ReceptionListCreate.as_view(), name='reception-list-create'),
    path('receptions/<str:pk>/', ReceptionDetail.as_view(), name='reception-detail'),

    # Routes pour Facture
    path('factures/', FactureListCreate.as_view(), name='facture-list-create'),
    path('factures/<str:pk>/', FactureDetail.as_view(), name='facture-detail'),

    # Routes pour Facturation
    path('facturations/', FacturationListCreate.as_view(), name='facturation-list-create'),
    path('facturations/<str:pk>/', FacturationDetail.as_view(), name='facturation-detail'),

    # Routes pour Achat
    path('achats/', AchatListCreate.as_view(), name='achat-list-create'),
    path('achats/<str:pk>/', AchatDetail.as_view(), name='achat-detail'),
]
