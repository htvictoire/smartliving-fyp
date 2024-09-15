import json
from django.utils import timezone
from .models import Energy
from datetime import timedelta
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from gpio.models import Pins
def register_energy_consumption(pin):
    if pin.state == 1:
        pin.last_on = timezone.now()
        pin.save()
    else:
        pin.last_off = timezone.now()
        pin.save()
        duration = pin.last_off - pin.last_on

        Energy.objects.create(pin=pin, date=timezone.now().date(), temps=duration)
    


def get_last_twenty_days_enregy_consumption(pins):
    today = timezone.now().date()
    last_twenty_days_dates = [today - timedelta(days=i) for i in range(19, -1, -1)]
    dates_data = []
    energy_data = []
    for d in last_twenty_days_dates:
        # convert the date in a readable format withe month and day like "Apr 19" , "May 1" etc
        str_date = d.strftime("%b %d")
        dates_data.append(str_date)

        total_duration = Energy.objects.filter(pin__in=pins, date=d).aggregate(total_duration=models.Sum('temps'))['total_duration']
        if len(pins) > 1:
            total_pin_power = pins.aggregate(total_power=models.Sum('power'))['total_power']
        else:
            total_pin_power = pins[0].power
        if total_duration is None:
            total_duration = timedelta()
            energy_data.append(0)
        else:
            energy_data.append(round((total_duration.total_seconds()/3600) * (total_pin_power/1000),2)) # energy in Kwh

    
    json_dates_data = json.dumps(dates_data)
    json_energy_data = json.dumps(energy_data)
        
    return json_dates_data, json_energy_data,  (today-timedelta(days=19)).strftime("%b %d"), today.strftime("%b %d")







def energy_consumption_control(pin):
    
    total_duration = Energy.objects.filter(pin=pin, date=timezone.now().date()).aggregate(total_duration=models.Sum('temps'))['total_duration']
    if total_duration is None:
        total_duration = timedelta()  
    
    total_power_used = ((total_duration.total_seconds() / 3600)/1000 ) * pin.power 
    consom_max = pin.consom_max
    
    if total_power_used > consom_max:
        if pin.control_mode: 
            pin.state = 0
            pin.save()
        else:
            if not pin.today_limit_reached:
                try:
                    send_mail(
                        'Energy Consumption Control',
                        f'The energy limit of {pin.nom} has been reached! \n Please turn it off or increase its consumption limit. \n\nThe system will turn it off automatically after 1 hour . \n\n Thank you!',
                        settings.EMAIL_HOST_USER,
                        [pin.user.email],
                        fail_silently=False,
                    )
                    pin.today_limit_reached = True
                    pin.save()
                except Exception as e:
                    print(e)


def reset_today_limit():
    now = timezone.now()
    if now.hour == 0 and now.minute <= 5 :
        for pin in Pins.objects.all():
            if pin.today_limit_reached:
                pin.today_limit_reached = False
                pin.save()