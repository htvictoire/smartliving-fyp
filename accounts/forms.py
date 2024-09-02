from django.forms import ModelForm,  TextInput, FileInput
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from django.db import models

from django.contrib.auth.forms import PasswordResetForm 
from django.contrib.auth.forms import SetPasswordForm 
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import User

User = get_user_model()

from django.shortcuts import render, redirect



##################################################




class SignUpForm(UserCreationForm):  #creation user etudiant
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2'] #ne pas oublier a customiser le message d'erreur pour email lors du template

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée. Veuillez utiliser une autre.")
        return email



#################################################





########################
class CustomSetPasswordForm(SetPasswordForm):      #reset password dans le processus de reinitialisation
    # Personnalisez les champs si nécessaire
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-transparent', 'place-holder': 'Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-transparent', 'place-holder': 'Confirm Password'})
    )




########################################################################



class StudentPasswordForm(PasswordChangeForm):    #changer mot de passe user etudiant dans profil
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'



