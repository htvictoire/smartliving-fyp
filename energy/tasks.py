from django.utils import timezone
from .models import Energy
from datetime import timedelta
from django.db import models
from .models import Notification

def calculate_energy_consumption(pin):
    if pin.state == 1:
        pin.last_on = timezone.now()
        pin.save()
    else:
        pin.last_off = timezone.now()
        pin.save()
        duration = pin.last_off - pin.last_on

        Energy.objects.create(pin=pin, date=timezone.now().date(), temps=duration)
        
        # consommation totale
        total_duration = Energy.objects.filter(pin=pin).aggregate(total_duration=models.Sum('temps'))['total_duration']
        if total_duration is None:
            total_duration = timedelta()  
        
        total_power_used = (total_duration.total_seconds() / 3600) * pin.power 
        consom_max = pin.consom_max
        
        if total_power_used > consom_max:
            if pin.control_mode: 
                pin.state = 0
                pin.save()
            else:
                Notification.objects.create(
                    pin=pin,
                    message="Energy limit reached",
                    type="alert"  
                )
        if total_power_used == (8/10)*consom_max:
            if pin.control_mode: 
                pin.state = 0
                pin.save()
            else:
                Notification.objects.create(
                    pin=pin,
                    message="80% Energy limit reached",
                    type="warning" 
                )