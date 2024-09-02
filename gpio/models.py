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
    fav = models.BooleanField(default=False)
    GPIO_CHOICES = {
        1 :"1",
        2 :"2",
        3 :"3",
        4 :"4",
        5 :"5",
    }
    gpio = models.IntegerField()
    state = models.IntegerField()
    

    class Meta:
        unique_together = ('board', 'gpio')
    
    def __str__(self):
        return f'for {self.nom}: on {self.board}'





class Messages(models.Model):
    message = models.TextField()
    recipient = models.CharField(max_length=13)
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
