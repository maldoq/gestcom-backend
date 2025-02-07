from django.urls import path
from .views import RegisterView, LoginView, ProfileView, BoutiqueView, UpdateModesPaiementView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('boutiques/', BoutiqueView.as_view(), name='boutiques-list-create'),
    path('boutiques/<int:boutique_id>/', BoutiqueView.as_view(), name='boutique-detail'),
    path('clients/', ClientView.as_view(), name='clients'),  # GET : Lister les clients | POST : Créer un client
    path('client/<int:client_id>/', ClientView.as_view(), name='client'),  # PUT : Modifier un client | DELETE : Supprimer un client
    path('reapprovisionnements/', ReapprovisionnementView.as_view(), name='liste-reapprovisionnements'),  # GET : Lister | POST : Créer
    path('reapprovisionnement/<int:idReap>/', ReapprovisionnementView.as_view(), name='reapprovisionnement'),  # PUT : Modifier | DELETE : Supprimer
]