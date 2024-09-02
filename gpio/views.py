from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Board, Pins, Messages, Places
from django.shortcuts import render, redirect, get_object_or_404
from accounts.views import get_fav_bar, get_nav_bar
from .forms import PinForm, PlaceForm, AntityForm
from django.views import View
from .chekers import check_place_manager, check_antity_manager

from accounts.models import User

import random

'''
@csrf_exempt
def etat_outputs(request, board_id):
    if request.method == 'GET':
        outputs = Pins.objects.filter(board__numero=board_id)
        output_states = {output.gpio: str(output.state) for output in outputs}
        return JsonResponse(output_states)
'''


@csrf_exempt
def etat_outputs(request, board_id):
    if request.method == 'GET':
        outputs = Pins.objects.filter(board__numero=board_id)
        output_states = [
            {
                'gpio': output.gpio,
                'state': str(output.state),
                'id': output.id,
            }
            for output in outputs
        ]
        return JsonResponse(output_states, safe=False)

'''
@csrf_exempt
def messages(request):
    if request.method == 'GET':
        messages_ = Messages.objects.filter(sent = False)
        messagess = {message.recipient: str(message.message) for message in messages_}
        return JsonResponse(messagess)
'''
def messages(request):
    if request.method == 'GET':
        messages_ = Messages.objects.filter(sent=False)
        messagess = [
            {
                'recipient': message.recipient,
                'message': str(message.message),
                'id': str(message.id)

            }
            for message in messages_
        ]
        return JsonResponse(messagess, safe=False)


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

    def get_nav_and_fav_pins(self, board=None):
        """Set up the navigation and favorite pins context."""
        nav_context = get_nav_bar(user=self.user, board=board)
        fav_pins = get_fav_bar(self.user)
        if isinstance(nav_context, tuple):
            nav_context = nav_context[0]
        self.context.update(nav_context)
        self.context['fav_pins'] = fav_pins




class PinsView(BaseView):
    """View for displaying pins related to a board."""
    template_name = 'gpio/pins.html'

    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        self.get_nav_and_fav_pins(board=board)
        board_pins = []

        if board in self.user.boards.all() or board in Board.objects.filter(place__in=self.user.places.all()):
            board_pins.extend(Pins.objects.filter(board=board))
            for p in board_pins:
                p.manager = True
        else:
            for pin in self.user.pins.filter(board=board):
                board_pins.append(pin)
                p.manager = False

        self.context.update({
            "pin_is_active" : True,
            "board_id": board_id,
            "pins": board_pins,
        })
        return render(request, self.template_name, self.context)




class CreatePinView(BaseView):
    """View for creating a new pin."""
    template_name = 'gpio/pin.html'
    form_class = PinForm

    def get(self, request):
        if not (self.user.place_manager or self.user.antity_manager):
            return redirect('login')

        self.get_nav_and_fav_pins()
        form = self.form_class(user=self.user)
        self.context.update({
            "pin_is_active" : True,
            'form': form,
            'pin_is_active': True,
            'title': "Add an Object",
            'description': "Add a physical object to an Antity",
        })
        return render(request, self.template_name, self.context)

    def post(self, request):
        if not (self.user.place_manager or self.user.antity_manager):
            return redirect('login')

        form = self.form_class(request.POST, user=self.user)
        if form.is_valid():
            pin = form.save(commit=False)
            pin.state = 0
            pin.save()
            return redirect('objects')
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

        self.get_nav_and_fav_pins()
        form = self.form_class(instance=pin, user=self.user)
        self.context.update({
            "pin_is_active" : True,
            'form': form,
            'pin_is_active': True,
            'title': f"Manage {pin.nom} from {pin.board.nom}",
            'description': "blablaba balab dvhfw",
        })
        return render(request, self.template_name, self.context)

    def post(self, request, pin_id):
        pin = get_object_or_404(Pins, id=pin_id)
        if not (self.user.place_manager or self.user.antity_manager and check_antity_manager(user=self.user, antity=pin.board)):
            return redirect('dashboard')

        form = self.form_class(request.POST, instance=pin, user=self.user)
        if form.is_valid():
            form.save()
            return redirect('objects')
        return self.get(request, pin_id=pin_id)






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
        
        
        self.get_nav_and_fav_pins() # call it before accessing the context key "all_boards"
        
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
            "title": "My places",
            "description": "blablaba balab dvhfw",
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

        self.get_nav_and_fav_pins()
        form = self.form_class(user=self.user)
        self.context.update({
            "board_is_active" : True,
            'form': form,
            'title': "Add an Antity",
            'description': "Add an Antity",
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
        if not check_place_manager(user=self.user, place=board.place):
            return redirect('dashboard')

        self.get_nav_and_fav_pins()
        form = self.form_class(instance=board, user=self.user)
        self.context.update({
            'form': form,
            'bord_is_active': True,
            'title': f"Manage {board.nom} from {board.place.nom}",
            'description': "blablaba balab dvhfw",
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







class PlacesView(BaseView):
    """View for displaying the user's places."""
    template_name = 'gpio/places.html'

    def get(self, request):
        if not check_place_manager(user=self.user, place=None):
            return redirect('dashboard')
        
        userplaces = self.user.places.all()
        for place in userplaces:
            place.name = place.nom.capitalize()
            place.first_letter = place.nom[0].upper()
            #place.bg_color = f"{'#%06x' % random.randint(0, 0xFFFFFF)}"
            place.bg_color = generate_dark_color()
            place.antity_number = Board.objects.filter(place=place).count()
            place.objects_number = Pins.objects.filter(board__place=place).count()


        self.get_nav_and_fav_pins()
        self.context.update({
            "place_is_active": True,
            "title": "My places",
            "description": "blablaba balab dvhfw",
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

        self.get_nav_and_fav_pins()
        form = self.form_class()
        self.context.update({
            "place_is_active" : True,
            'form': form,
            'title': "Add a Locaton",
            'description': "Add an Antity",
        })
        return render(request, self.template_name, self.context)

    def post(self, request):
        if not (self.user.place_manager):
            return redirect('login')

        form = self.form_class(request.POST)
        if form.is_valid():
            place = form.save(commit=False)
            place.save()
            self.user.places.add(place)
            return redirect('my_places')
        return self.get(request)




class ManagePlaceView(BaseView):
    """View for managing a place."""
    template_name = 'gpio/place.html'
    form_class = PlaceForm

    def get(self, request, place_id):
        place = get_object_or_404(Places, id=place_id)
        if not (self.user.place_manager) or not check_place_manager(user=self.user, place=place):
            return redirect('login')
        form = self.form_class(instance=place)
        self.get_nav_and_fav_pins()
        self.context.update({
            "place_is_active" : True,
            'form': form,
            'title': "Add a Locaton",
            'description': "Add an Antity",
        })
        return render(request, self.template_name, self.context)

    def post(self, request, place_id):
        place = get_object_or_404(Places, id=place_id)
        form = self.form_class(request.POST, instance=place)
        if form.is_valid():
            form.save()
            return redirect('my_places')
        return self.get(request)

