from django.db import models
from django.urls import reverse

class Player(models.Model):
    name = models.CharField(max_length=200, unique=True)
    id = models.CharField(max_length=200, primary_key=True)
    elo = models.IntegerField(default=1500)
    def __str__(self):
        return self.name

class Card(models.Model):
    cutter = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="cards")
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Cut by {self.cutter} on {self.date}"

class Game(models.Model):
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="winners")
    winner_points = models.IntegerField(default=0)
    loser = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="losers")
    loser_points = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.winner.name + " beat " + self.loser.name
    def save(self, *args, **kwargs):
        if not self.pk:
            if self.winner.name == self.loser.name:
                return
            recalculate_elo(self.winner, self.loser)
        super(Game, self).save(*args, **kwargs)

def recalculate_elo(winner, loser, wk=24, lk=24):
    w = winner.elo
    l = loser.elo
    wg = winner.losers.count() + winner.winners.count()
    lg = loser.losers.count() + loser.winners.count()
    if wg <= 10:
        wk = 36
    if lg <= 10:
        lk = 36
    d = (w-l)/400
    we = 1 / (1 + 10**(-d))
    le = 1 / (1 + 10**(d))
    winner.elo = w + max(1, wk*(1-we))
    loser.elo = l - max(1, lk*le)
    winner.save()
    loser.save()

# Create your models here.
