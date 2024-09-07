
from django import forms

from .models import Board, Places, Pins



class PinForm(forms.ModelForm):
    class Meta:
        model = Pins
        fields = ['nom', 'board', 'gpio']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
            'gpio': forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'board': forms.Select(attrs={'class': 'form-control form-control-solid'})
        }

    def __init__(self,  *args, user= None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            boards = []
            boards.extend(user.boards.all())
            boards.extend( Board.objects.filter(place__in = user.places.all()).exclude(id__in = [b.id for b in boards]))
            boards = Board.objects.filter(id__in = [b.id for b in boards])
            self.fields['board'].queryset = boards





class AntityForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['nom', 'place', 'code']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
            'code': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
            'place': forms.Select(attrs={'class': 'form-control form-control-solid'})
        }
    
    def __init__(self,  *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields['place'].queryset = user.places.all()




class PlaceForm(forms.ModelForm):
    class Meta:
        model = Places
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
        }
