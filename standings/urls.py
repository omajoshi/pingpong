from django.urls import path
from . import views

app_name = 'standings'

urlpatterns = [
    path('pingpong/', views.PingPongIndexView.as_view(), name='pindex'),
    path('pingpong/elo/', views.PingPongIndexView.as_view(), name='elo'),
    path('create/', views.create, name='create'),
    path('pingpong/games/', views.GamesView.as_view(), name='games'),
    path('pingpong/<player>/', views.PlayerView.as_view(), name='player'),
    path('cut/', views.cut_cards, name='cut'),
    path('', views.CardIndexView.as_view(), name='cindex'),

]
