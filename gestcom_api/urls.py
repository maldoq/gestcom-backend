from django.urls import path
from .views import RegisterView, LoginView, ProfileView, CreateBoutiqueView, ListBoutiquesView, UpdateBoutiqueView, DeleteBoutiqueView, UpdateModesPaiementView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('boutique/creer/', CreateBoutiqueView.as_view(), name='creer_boutique'),
    path('boutiques/', ListBoutiquesView.as_view(), name='liste_boutiques'),
    path('boutique/modifier/<int:boutique_id>/', UpdateBoutiqueView.as_view(), name='modifier_boutique'),
    path('boutique/supprimer/<int:boutique_id>/', DeleteBoutiqueView.as_view(), name='supprimer_boutique'),
    path('boutique/modes-paiement/<int:boutique_id>/', UpdateModesPaiementView.as_view(), name='modes_paiement_boutique'),
]