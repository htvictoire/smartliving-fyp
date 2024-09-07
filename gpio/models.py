from django.db import models





class Places(models.Model):
    nom = models.CharField(max_length=255, unique=True, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255, unique=True, null=False, blank=False)

    def __str__(self):
        return self.nom
    





class Board(models.Model):   # Entities
    nom = models.CharField(max_length=255,unique=True, null=True, blank=False)
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
    

    class Meta:
        unique_together = ('board', 'gpio')
    
    def __str__(self):
        return f'for {self.nom}: on {self.board}'



