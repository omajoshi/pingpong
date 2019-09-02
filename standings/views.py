import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.template import loader
from .models import Player, Game
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

class IndexView(generic.ListView):
    template_name = 'standings/index.html'
    context_object_name = 'standings'
    def get_queryset(self):
        return Player.objects.annotate(wins=Count('winners', distinct=True), losses=Count('losers', distinct=True)).order_by('-elo')

class GamesView(generic.ListView):
    template_name = 'standings/games.html'
    context_object_name = 'games'
    def get_queryset(self):
        return Game.objects.order_by('-date')


class PlayerView(generic.ListView):
    template_name = 'standings/games_player.html'
    context_object_name = 'games'
    def get_queryset(self):
        player = Player.objects.get(name=self.kwargs['player'])
        return Game.objects.filter(Q(winner=player) | Q(loser=player)).order_by('-date')
    def get_context_data(self):
        context = super().get_context_data(**self.kwargs)
        context['player'] = self.kwargs['player']
        return context

@csrf_exempt
def create(request):
    if request.method == "GET":
        return redirect('standings:index')
    if request.method == "POST":
        command = request.POST.get('command')
        if command == "/add":
            text = request.POST['text']
            try:
                info = re.search(r"<@(?P<id>.*?)\|(?P<name>.*?)>", text).groupdict()
            except AttributeError:
                return HttpResponse("That didn't work. Try `/add @player`")
            p, new = Player.objects.get_or_create(id=info['id'])
            p.name = info['name']
            p.save()
            return JsonResponse({"response_type": "in_channel", "text": f"{p.name} ({p.elo})"})
        if command == "/update":
            text = request.POST['text']
            try:
                info = re.search(r"<@(?P<id>.*?)\|(?P<name>.*?)> (?P<elo>[0-9]*)", text).groupdict()
            except AttributeError:
                return HttpResponse("That didn't work. Try `/update @player 1500`")
            p, new = Player.objects.get_or_create(id=info['id'])
            p.name = info['name']
            p.elo = info['elo']
            p.save()
            return JsonResponse({"response_type": "in_channel", "text": f"{p.name} ({p.elo})"})

        if command == "/game":
            text = request.POST['text']
            try:
                info = re.search(r"<@(?P<w_id>.*?)\|(?P<w_name>.*?)> <@(?P<l_id>.*?)\|(?P<l_name>.*?)>", text).groupdict()
            except AttributeError:
                return HttpResponse("That didn't work. Try `/game @winner @loser`")
            w, new = Player.objects.get_or_create(id=info['w_id'])
            w.name = info['w_name']
            w.save()
            l, new = Player.objects.get_or_create(id=info['l_id'])
            l.name = info['l_name']
            l.save()
            Game.objects.create(winner=w, loser=l)
            return JsonResponse({"response_type": "in_channel", "text": f"{w.name} beats {l.name}"})
        if command == "/standings":
            return JsonResponse({"response_type": "in_channel", "text": "\n".join([f"{i+1}. {player.name} ({player.elo})" for i, player in enumerate(Player.objects.order_by('-elo'))])})
        return HttpResponse("You did something wrong.")