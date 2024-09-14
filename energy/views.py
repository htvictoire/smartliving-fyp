from django.shortcuts import render
from .models import Notification
from django.views.generic import TemplateView
from .models import Energy
from gpio.models import Places, Board
from django.db.models import Sum
from datetime import timedelta
from django.http import JsonResponse

def notif(request):
    notifications = Notification.objects.filter(user=request.user) 
    context={'notifications': notifications}
    return render(request, 'accounts/header.html',context )


class EnergyReportJsonView(TemplateView):
    def get(self, request, *args, **kwargs):
        places = Places.objects.all()
        report_data = []

        for place in places:
            place_boards = place.board_set.all()
            place_total_energy = 0
            boards_data = []

            for board in place_boards:
                board_pins = board.pins_set.all()
                board_total_energy = 0
                pins_data = []

                for pin in board_pins:
                    total_pin_time = Energy.objects.filter(pin=pin).aggregate(total_time=Sum('temps'))['total_time'] or timedelta(0)
                    total_pin_time_seconds = total_pin_time.total_seconds()
                    total_pin_time_hours = total_pin_time_seconds / 3600
                    pin_energy = pin.power * total_pin_time_hours

                    pins_data.append({
                        'pin_nom': pin.nom,
                        'energy': pin_energy
                    })

                    board_total_energy += pin_energy

                boards_data.append({
                    'board_nom': board.nom,
                    'total_energy': board_total_energy,
                    'pins': pins_data
                })
                place_total_energy += board_total_energy

            report_data.append({
                'place_nom': place.nom,
                'total_energy': place_total_energy,
                'boards': boards_data
            })

        return JsonResponse({'report_data': report_data})



class EnergyReportView(TemplateView):
    template_name = 'energy/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        places = Places.objects.all()
        report_data = []

        for place in places:
            place_boards = place.board_set.all()
            place_total_energy = 0
            boards_data = []

            for board in place_boards:
                board_pins = board.pins_set.all()
                board_total_energy = 0
                pins_data = []

                for pin in board_pins:
                    # Calculer la durée totale d'activation de la pin
                    total_pin_time = Energy.objects.filter(pin=pin).aggregate(total_time=Sum('temps'))['total_time'] or timedelta(0)
                    
                    # Convertir la durée en heures
                    total_pin_time_seconds = total_pin_time.total_seconds()  # en secondes
                    total_pin_time_hours = total_pin_time_seconds / 3600  # en heures
                    
                    # Calculer l'énergie consommée en kWh
                    pin_energy = pin.power * total_pin_time_hours
                    
                    # Ajouter les données de la pin
                    pins_data.append({
                        'pin': pin,
                        'energy': pin_energy
                    })
                    
                    # Ajouter l'énergie de la pin au total pour le board
                    board_total_energy += pin_energy

                # Ajouter les données du board
                boards_data.append({
                    'board': board,
                    'total_energy': board_total_energy,
                    'pins': pins_data
                })
                
                # Ajouter l'énergie totale du board à l'énergie de la place
                place_total_energy += board_total_energy

            # Ajouter les données de la place
            report_data.append({
                'place': place,
                'total_energy': place_total_energy,
                'boards': boards_data
            })

        context['report_data'] = report_data
        return context
