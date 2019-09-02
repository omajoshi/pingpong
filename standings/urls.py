from django.urls import path
from . import views

app_name = 'standings'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('elo/', views.IndexView.as_view(), name='elo'),
    path('create/', views.create, name='create'),
    path('games/', views.GamesView.as_view(), name='games'),
    path('<player>/', views.PlayerView.as_view(), name='player'),
]
