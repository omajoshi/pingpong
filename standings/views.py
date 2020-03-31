import re, requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.template import loader
from .models import Player, Game, Card
from django.db.models import Count, Q, Sum
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

class CardIndexView(generic.ListView):
    template_name = 'standings/cindex.html'
    context_object_name = 'standings'
    def get_queryset(self):
        return  Player.objects.annotate(cards_cut=Count('cards')).filter(cards_cut__gt=0).order_by('-cards_cut')


class PingPongIndexView(generic.ListView):
    template_name = 'standings/pindex.html'
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
def cut_cards(request):
    if request.method == "GET":
        return redirect('standings:cindex')
    if request.method == "POST":
        command = request.POST.get('command')
    if command == "/cards":
        text = request.POST.get('text')
        try:
            val = int(text)
        except:
            card_cutters = Player.objects.annotate(cards_cut=Count('cards')).filter(cards_cut__gt=0).order_by('-cards_cut')
            message = "No one has cut any cards!  Start cutting cards ..."
            if len(card_cutters):
                message = f"*TOTAL CARDS CUT: {Card.objects.count()}*\n" + "\n".join([f"{i+1}. {player.name} ({player.cards_cut})" for i, player in enumerate(card_cutters)])
            return JsonResponse({"response_type": "in_channel", "text": message})
        p, new = Player.objects.get_or_create(id=request.POST['user_id'])
        p.name = request.POST['user_name']
        p.save()
        if val > 0:
            for x in range(val):
                Card.objects.create(cutter=p)
            p.save()
            message = f"{p.name} cut {val} cards.  {p.name} now has cut a total of {p.cards.count()} cards."
            webhook_url = ""
            requests.post(webhook_url, json={'text': message})
        elif val + p.cards.count() >= 0:
            Card.objects.filter(id__in=list(p.cards.order_by('-date').values_list('pk', flat=True)[:-val])).delete()
            message = f"You subtracted {-val} cards from your total.  You now have cut a total of {p.cards.count()} cards."
        else:
            c = p.cards.count()
            p.cards.all().delete()
            message = f"You had {c} cards ... but you tried to subtract {-val}.  Your total number of cards cut has instead been set to zero."
        return JsonResponse({"response_type": "ephemeral", "text": message})
    return HttpResponse("You did something wrong.")


@csrf_exempt
def create(request):
    if request.method == "GET":
        return redirect('standings:pindex')
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
