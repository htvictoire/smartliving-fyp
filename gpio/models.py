from django.db import models
from django.conf import settings


class Places(models.Model):
    nom = models.CharField(max_length=255, unique=True, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255, unique=True, null=False, blank=False)

    def __str__(self):
        return self.nom
    

    
class Board(models.Model):
    nom = models.CharField(max_length=255, unique=True, null=True, blank=False)
    place = models.ForeignKey(Places, null=False, blank=False, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.code} for {self.nom}'



class Pins(models.Model):
    nom = models.CharField(max_length=255, null=True, blank=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    GPIO_CHOICES = {
        1 :"12",
        2 :"16",
        3 :"22",
        4 :"28",
        5 :"34",
    }
    gpio = models.IntegerField(choices=GPIO_CHOICES, null=True, blank=False)
    state = models.IntegerField()
    
    power = models.FloatField()
    consom_max = models.FloatField(default=100000000000.0)
    last_on = models.DateTimeField(null=True, blank=True)
    last_off = models.DateTimeField(null=True, blank=True)
    control_mode = models.BooleanField(default=False)
    today_limit_reached = models.BooleanField(default=False)
    class Meta:
        unique_together = ('board', 'gpio')
    
    def __str__(self):
        return f'for {self.nom}: on {self.board}'




class MessageBoard(models.Model):
    tel_num = models.CharField(max_length=20, null=True, blank=True, unique=True)
    code = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  # Ajout d'un related_name unique

    def __str__(self):
        return f'{self.code} for {self.user}'