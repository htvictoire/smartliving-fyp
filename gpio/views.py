from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Board, Pins, Places, MessageBoard
from accounts.models import Messages, Favorites
from django.shortcuts import render, redirect, get_object_or_404
from accounts.views import get_fav_bar, get_nav_bar
from .forms import PinForm, PlaceForm, AntityForm
from django.views import View
from .chekers import check_place_manager, check_antity_manager
from energy.tasks import register_energy_consumption, get_last_twenty_days_enregy_consumption
from energy.models import Notification
from django.utils import timezone
from datetime import timedelta

import random


import json
'''
@csrf_exempt
def etat_outputs(request, board_id):
    if request.method == 'GET':
        outputs = Pins.objects.filter(board__numero=board_id)
        output_states = {output.gpio: str(output.state) for output in outputs}
        return JsonResponse(output_states)
'''


@csrf_exempt
def etat_outputs(request, board_code):
    if request.method == 'GET':
        outputs = Pins.objects.filter(board__code=board_code)
        output_states = {output.gpio: str(output.state) for output in outputs}
        return JsonResponse(output_states)



'''def messages(request):
    if request.method == 'GET':
        messages = Messages.objects.filter(sent=False)
        messagess = [
            {
                'recipient': message.recipient,
                'message': str(message.message),
                'id': str(message.id)

            }
            for message in messages
        ]
        for m in messages:
            m.sent = True
            m.save()
        return JsonResponse(messagess, safe=False) '''








# for ui auto update
def check_pin_state(request):
    pin_id = request.GET.get('pin_id')
    pin = get_object_or_404(Pins, id=pin_id)
    return JsonResponse({'state': pin.state})




@csrf_exempt
@require_POST
def switch_on(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        pin_id = data.get('pin_id')
        pin = Pins.objects.get(id=pin_id)
        pin.state = 0
        pin.save()
        if pin.state == 1:
            register_energy_consumption(pin)
        return JsonResponse({'status': 'success', 'state': pin.state})
    except Pins.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pin not found'}, status=404)
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

@csrf_exempt
@require_POST
def switch_off(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        pin_id = data.get('pin_id')
        pin = Pins.objects.get(id=pin_id)
        pin.state = 1
        pin.save()
        if pin.state == 0:
            register_energy_consumption(pin)
        return JsonResponse({'status': 'success', 'state': pin.state})
    except Pins.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pin not found'}, status=404)
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)








@csrf_exempt
def update_messages(request, message_id):
    message = Messages.objects.get(id=message_id)
    message.sent = True




@csrf_exempt
def handle_output_create(request):
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        board_id = data.get('board')
        gpio = data.get('gpio')
        state = data.get('state')

        board, created = Board.objects.get_or_create(board_id=board_id)
        output, created = Output.objects.get_or_create(name=name, board=board, gpio=gpio, state=state)

        return JsonResponse({'result': 'success'})






class BaseView(View):
    """Base view for pin-related operations to avoid code repetition."""
    template_name = None
    form_class = None

    def dispatch(self, request, *args, **kwargs):
        """Initialize common attributes before dispatching the request."""
        self.user = request.user
        self.context = {}
        return super().dispatch(request, *args, **kwargs)

    def get_nav_and_fav_pins_notifs(self, board=None):
        """Set up the navigation and favorite pins context."""
        notifications = Notification.objects.filter(user=self.user).order_by('-created_at')
        nav_context = get_nav_bar(user=self.user, board=board)
        fav_pins = get_fav_bar(self.user)
        if isinstance(nav_context, tuple):
            nav_context = nav_context[0]
        self.context.update(nav_context)
        self.context['fav_pins'] = fav_pins
        self.context['notifications'] = notifications




class PinsView(BaseView):
    """View for displaying pins related to a board."""
    template_name = 'gpio/pins.html'

    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        self.get_nav_and_fav_pins_notifs(board=board)
        board_pins = []

        if board in self.user.boards.all() or board in Board.objects.filter(place__in=self.user.places.all()):
            board_pins.extend(Pins.objects.filter(board=board))
            for p in board_pins:
                p.manager = True
        else:
            for pin in self.user.pins.filter(board=board):
                board_pins.append(pin)
                pin.manager = False

        self.context.update({
            "board_id": board_id,
            "pins": board_pins,
            })
        return render(request, self.template_name, self.context)



@csrf_exempt
def get_available_gpios(request):
    if request.method == 'POST':
        board_id = request.POST.get('board_id')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return JsonResponse({'error': 'Board not found'}, status=404)

        # Get all GPIO pins already used on the selected board
        used_gpios = Pins.objects.filter(board=board).values_list('gpio', flat=True)

        # Define all possible GPIO options
        GPIO_CHOICES = {
            1: "12",
            2: "16",
            3: "22",
            4: "28",
            5: "34",
        }

        # Filter out GPIOs that are already used
        available_gpios = {key: value for key, value in GPIO_CHOICES.items() if key not in used_gpios}

        if not available_gpios:
            return JsonResponse({'message': 'No available GPIO pins on this board'}, status=200)

        return JsonResponse({'available_gpios': available_gpios}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)



class CreatePinView(BaseView):
    """View for creating a new pin."""
    template_name = 'gpio/pin.html'
    form_class = PinForm

    def get(self, request):
        if not (self.user.place_manager or self.user.antity_manager):
            return redirect('login')

        self.get_nav_and_fav_pins_notifs()
        form = self.form_class(user=self.user)
        self.context.update({
            'form': form,
            'pin_is_active': True,
            'title': "Add an Object",
            'description': "Add a physical object representation to an Entity",
        })
        return render(request, self.template_name, self.context)

    def post(self, request):
        if not (self.user.place_manager or self.user.antity_manager):
            return redirect('login')

        form = self.form_class(request.POST, user=self.user)
        favorite = request.POST.get('favorite', False)
        control_mode = request.POST.get('strict', False)
        if form.is_valid():
            pin = form.save(commit=False)
            pin.state = 0
            pin.control_mode = control_mode
            pin.save()
            if favorite:
                Favorites.objects.create(user=self.user, pin=pin)
                _favs = Favorites.objects.filter(user=self.user).order_by('-update_time')
                if len(_favs ) > 5:
                    _favs.last().delete()
            return redirect('objects', board_id=pin.board.id)
        return self.get(request)




class ManagePinView(BaseView):
    """View for managing an existing pin."""
    template_name = 'gpio/pin.html'
    form_class = PinForm

    def get(self, request, pin_id):
        if not (self.user.place_manager or self.user.antity_manager):
            return redirect('login')

        pin = get_object_or_404(Pins, id=pin_id)
        if not check_antity_manager(user=self.user, antity=pin.board):
            return redirect('dashboard')

        self.get_nav_and_fav_pins_notifs(board=pin.board)

        dates_data, energy_data, past_date, today = get_last_twenty_days_enregy_consumption(pins=[pin])

        form = self.form_class(instance=pin, user=self.user)
        fav_check = Favorites.objects.filter(user=self.user, pin=pin).exists()
        strict_check = pin.control_mode

        self.context.update({
            'dates_data': dates_data,
            'energy_data': energy_data,
            'past_date': past_date,
            'today': today,
            'form': form,
            'fav_check' : fav_check,
            'strict_check': strict_check,
            'title': f"Manage {pin.nom} from {pin.board.nom} at {pin.board.place.nom}",
            'description': "Edit or delete the object, View its energy consumption report",
            "management" : True
        })
        return render(request, self.template_name, self.context)

    def post(self, request, pin_id):
        pin = get_object_or_404(Pins, id=pin_id)
        if not (self.user.place_manager or self.user.antity_manager and check_antity_manager(user=self.user, antity=pin.board)):
            return redirect('dashboard')

        form = self.form_class(request.POST, instance=pin, user=self.user)
        favorite = request.POST.get('favorite', False)
        control_mode = request.POST.get('strict', False)
        if control_mode == 'on':
            control_mode = True
        else:
            control_mode = False
        if form.is_valid():
            pin = form.save(commit=False)
            pin.state = 0
            pin.control_mode = control_mode
            pin.save()
            if favorite:
                is_fav_pin , created = Favorites.objects.get_or_create(user=self.user, pin=pin)
                if created:

                    print("\n\nTTTTTTTTTTRRRRRRRRUUU\n\n")
                    _favs = Favorites.objects.filter(user=self.user).order_by('-update_time')
                    if len(_favs ) > 5:
                        _favs.last().delete()
            else:
                if Favorites.objects.filter(user=self.user, pin=pin).exists():
                    Favorites.objects.get(user=self.user, pin=pin).delete()
            form.save()
            return redirect('objects', board_id=pin.board.id)
        return self.get(request, pin_id=pin_id)


def delete_object(request, pin_id):
    Pins.objects.get(id=pin_id).delete()
    favs = Favorites.objects.filter(pin__id=pin_id)
    if favs:
        for f in favs:
            f.delete()
    return redirect('my_antities')





def generate_dark_color():
    r = random.randint(0, 127)  # Red component
    g = random.randint(0, 127)  # Green component
    b = random.randint(0, 127)  # Blue component
    return f"#{r:02x}{g:02x}{b:02x}"





class AntitiesView(BaseView):
    """View for displaying the user's antities."""
    template_name = 'gpio/antities.html'

    def get(self, request):
        if not check_antity_manager(user=self.user, antity=None):
            return redirect('dashboard')


        self.get_nav_and_fav_pins_notifs() # call it before accessing the context key "all_boards"

        userantities = self.context['all_boards']
        for board in userantities:
            board.name = board.nom.capitalize()
            board.first_letter = board.nom[0].upper()
            #place.bg_color = f"{'#%06x' % random.randint(0, 0xFFFFFF)}"
            board.bg_color = generate_dark_color()
            board.objects_number = Pins.objects.filter(board=board).count()


        self.context.update({
            "board_is_active": True,
            "place_manager" : self.user.place_manager,
            "title": "My Entities",
            "description": "An entity is a part of a location coresponding to a single board",
            "userantities": userantities,
        })
        return render(request, self.template_name, self.context)






class CreateAntityView(BaseView):
    """View for creating a new pin."""
    template_name = 'gpio/board.html'
    form_class = AntityForm

    def get(self, request):
        if not (self.user.place_manager):
            return redirect('login')

        self.get_nav_and_fav_pins_notifs()
        form = self.form_class(user=self.user)
        self.context.update({
            "board_is_active": True,
            'form': form,
            'title': "Add an Entity",
            'description': "The code of the entity will be used by the board to acces its data",
        })
        return render(request, self.template_name, self.context)

    def post(self, request):
        if not (self.user.place_manager):
            return redirect('login')

        form = self.form_class(request.POST, user=self.user)
        if form.is_valid():
            board = form.save(commit=False)
            ##
            board.save()
            return redirect('my_antities')
        return self.get(request)



class ManageAntityView(BaseView):
    """View for managing an existing pin."""
    template_name = 'gpio/board.html'
    form_class = AntityForm

    def get(self, request, board_id):
        if not (self.user.place_manager):
            return redirect('login')
        board = get_object_or_404(Board, id=board_id)
        pins = Pins.objects.filter(board=board)
        if not check_place_manager(user=self.user, place=board.place):
            return redirect('dashboard')

        self.get_nav_and_fav_pins_notifs()
        form = self.form_class(instance=board, user=self.user)
        if pins:
            dates_data, energy_data, past_date, today = get_last_twenty_days_enregy_consumption(pins)
        else :
            dates_data, energy_data, past_date, today = None, None, None, None

        print(f'{dates_data}\n\n{energy_data}\n\n{past_date , today}')

        self.context.update({
            "board_is_active": True,
            'form': form,
            "management": True,
            'bord_is_active': True,
            'title': f"Manage {board.nom} from {board.place.nom}",
            'description': "Edit or delete the entity, View its energy report",
            'dates_data': dates_data,
            'energy_data': energy_data,
            'past_date': past_date,
            'today': today,
            'have_pins': pins,
        })
        return render(request, self.template_name, self.context)


    def post(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        if not (self.user.place_manager):
            return redirect('dashboard')

        form = self.form_class(request.POST, instance=board, user=self.user)
        if form.is_valid():
            form.save()
            return redirect('my_antities')
        return self.get(request, board_id=board_id)



def delete_antity(request, board_id):
    antity = Board.objects.get(id=board_id)
    pins = Pins.objects.filter(board=antity)

    for pin in pins:
        favs = Favorites.objects.filter(pin=pin)
        if favs:
            for f in favs:
                f.delete()
        pin.delete()
    antity.delete()
    return redirect('my_antities')





class PlacesView(BaseView):
    """View for displaying the user's places."""
    template_name = 'gpio/places.html'

    def get(self, request):
        # no need to check if he is a place manager because every one ca create a place
        userplaces = self.user.places.all()
        for place in userplaces:
            place.name = place.nom.capitalize()
            place.first_letter = place.nom[0].upper()
            #place.bg_color = f"{'#%06x' % random.randint(0, 0xFFFFFF)}"
            place.bg_color = generate_dark_color()
            place.antity_number = Board.objects.filter(place=place).count()
            place.objects_number = Pins.objects.filter(board__place=place).count()


        self.get_nav_and_fav_pins_notifs()
        self.context.update({
            "place_is_active": True,
            "title": "My places",
            "description": "The list of places or locations you can manage, click on add a place to add one.",
            "userplaces": userplaces,
        })
        return render(request, self.template_name, self.context)




class CreatePlaceView(BaseView):
    """View for creating a new location."""
    template_name = 'gpio/place.html'
    form_class = PlaceForm

    def get(self, request):
        if not (self.user.place_manager):
            return redirect('login')

        self.get_nav_and_fav_pins_notifs()
        form = self.form_class()
        self.context.update({
            "place_is_active" : True,
            'form': form,
            'title': "Add a Place",
            'description': "Add a Location , the required fields are marked with *",
        })
        return render(request, self.template_name, self.context)

    def post(self, request):

        form = self.form_class(request.POST)
        if form.is_valid():
            place = form.save(commit=False)
            place.save()
            self.user.place_manager = True
            self.user.places.add(place)
            self.user.save()
            return redirect('my_places')
        return self.get(request)




class ManagePlaceView(BaseView):
    """View for managing a place."""
    template_name = 'gpio/place.html'
    form_class = PlaceForm

    def get(self, request, place_id):
        place = get_object_or_404(Places, id=place_id)
        pins = Pins.objects.filter(board__place = place)
        if not (self.user.place_manager) or not check_place_manager(user=self.user, place=place):
            return redirect('login')
        form = self.form_class(instance=place)
        if pins:
            dates_data, energy_data, past_date, today = get_last_twenty_days_enregy_consumption(pins)
        else :
            dates_data, energy_data, past_date, today = None, None, None, None

        print(f'{dates_data}\n\n{energy_data}\n\n{past_date , today}')

        self.get_nav_and_fav_pins_notifs()
        self.context.update({
            "place_is_active" : True,
            "management": True,
            'form': form,
            'title': f"Manage {place.nom}",
            'description': "Edit or delete the Location, View its energy consumption report for the last 20 days ",
            'dates_data': dates_data,
            'energy_data': energy_data,
            'past_date': past_date,
            'today': today,
            'have_pins': pins,

        })
        return render(request, self.template_name, self.context)

    def post(self, request, place_id):
        place = get_object_or_404(Places, id=place_id)
        form = self.form_class(request.POST, instance=place)
        if form.is_valid():
            form.save()
            return redirect('my_places')
        return self.get(request)


def delete_place(request, place_id):
    place = Places.objects.get(id=place_id)
    antities = Board.objects.filter(place=place)
    pins = Pins.objects.filter(board__place=place)
    for pin in pins:
        favs = Favorites.objects.filter(pin=pin)
        if favs:
            for f in favs:
                f.delete()
        pin.delete()
        pin.delete()
    for antity in antities:
        antity.delete()
    place.delete()
    return redirect('my_places')





class SendMessageView(BaseView):
    template_name = 'gpio/sendmessage.html'
    def get(self, request):
        user = request.user
        user_boards = MessageBoard.objects.filter(user=user)
        if not user_boards:
            return redirect('dashboard')
        if len(user_boards) > 1:
            many_boards = True
            boards = user_boards
        else:
            boards = None
            many_boards = False
        self.context.update({
            'many_boards': many_boards,
            'boards': boards
        })

        return render(request, self.template_name, self.context)
    def post(self, request):
        if request.method == 'POST':
            message_body = request.POST.get('message')
            phone_number = request.POST.get('phone_number')

            if len(user_boards = MessageBoard.objects.filter(user=request.user)) > 1:
                board_id = request.POST.get('board_code')
            else:
                board_id = MessageBoard.objects.get(user=request.user).id


            if not message_body or not phone_number:
                return JsonResponse({'error': 'Please fil all the fields'}, status=400)

            Messages.objects.create(
                message=message_body,
                sender=request.user.email,
                receiver=phone_number,
                out=True,
                board=MessageBoard.objects.get(id=board_id)
            )
            return redirect('messages')



class MyMessagesView(BaseView):
    template_name = 'gpio/messages.html'
    def get(self, request):
        user_boards = MessageBoard.objects.filter(user=request.user)

        conversations = Messages.objects.filter(board__in=user_boards).order_by('created_at')

        self.context.update({
            'conversations': conversations
        })
        return render(request, self.template_name , self.context)


def receive_messages(request):
    if request.method == 'POST':
        message_body = request.POST.get('message')
        phone_number = request.POST.get('phone_number')
        board_code = request.POST.get('board_code')
        Messages.objects.create(
            message=message_body,
            sender=phone_number,
            receiver=MessageBoard.objects.get(code=board_code).user.email,
            out=False
        )
        return redirect('messages')


def send_message(request, board_code):
    if request.method == 'GET':
        board = MessageBoard.objects.get(code=board_code)
        messages = Messages.objects.filter(board=board, out=True, sent = False)
        messages = [
            {
                'number': m.receiver,
                'message': m.message
            }
            for m in messages
        ]
        return JsonResponse({'messages': messages}, safe=False)