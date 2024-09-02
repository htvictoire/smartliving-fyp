

from .models import Pins, Board, Places

'''
def check_pin_manager(user, pin):
    if pin in Pins.objects.filter(board__in = user.boards.all()) or pin in Pins.objects.filter(board__in = Board.objects.filter(place__in = user.places.all())) :
        return True
    else:
        return False


'''


# only antity and place manager, place manager can manage antities and antity can manage the pins of their antities




def check_antity_manager(user, antity):
    if antity == None:
        if user.antity_manager :
            return True
    else:
        if antity in Board.objects.filter(place__in = user.places.all()) or antity in user.boards.all():
            return True
        else : 
            return False


def check_place_manager(user, place):
    if place == None:
        if user.place_manager:
            return True
    else:
        if place in user.places.all():
            return True
        else : 
            return False
        