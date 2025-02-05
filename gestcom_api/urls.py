from django.urls import path
from .views import RoleListCreate, RoleDetail, CustomUserListCreate, CustomUserDetail, TypeListCreate, TypeDetail, BoutiqueListCreate, BoutiqueDetail, CategorieListCreate

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
]
