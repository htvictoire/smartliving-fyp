from django.db import models
from gpio.models import Pins
from accounts.models import User
# Create your models here.

class Energy(models.Model):   
    pin = models.ForeignKey(Pins, null=False, blank=False, on_delete=models.CASCADE)
    date = models.DateField()
    temps = models.DurationField()  

    def __str__(self):
        return f'{self.pin} used for {self.temps} on date {self.date}'

class Notification(models.Model):
    pin = models.ForeignKey(Pins, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.message
