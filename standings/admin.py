from django.contrib import admin

from .models import Game, Player, Card

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Card)
# Register your models here.
