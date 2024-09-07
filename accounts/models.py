from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from datetime import date , time
from gpio.models import Places, Board, Pins


from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user






class User(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(_('email address'), unique=True)
    last_password_reset_request = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False) # NIU (NOT IN USE)
    is_active = models.BooleanField(default=False)
    roll_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    verification_requests = models.PositiveIntegerField(default=0) 

    place_manager = models.BooleanField(default=False)
    places = models.ManyToManyField(Places, blank=True)

    antity_manager = models.BooleanField(default=False)
    boards  = models.ManyToManyField(Board, blank=True)

    pins = models.ManyToManyField(Pins, blank=True)



    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Administrateur"

    

class UserActivity(models.Model):    # pour ajouter a record for each action in all app views
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=1000)
    objet = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.objet} on {self.date}"


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin  = models.ForeignKey(Pins, on_delete=models.CASCADE)
    update_time = models.TimeField( auto_now=True, null=True)

    def __str__(self) :
        return f'{self.user}-{self.pin}'






class Messages(models.Model):
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    user_code = models.CharField(max_length=100, null=True, blank=False) # To pass to the link in the esp32 
    created_at = models.DateTimeField(auto_now_add=True)



from django.contrib.auth.backends import ModelBackend 

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username:
            try:
                # Try to match username as either email or roll_number
                user = User.objects.get(
                    models.Q(email=username) | models.Q(roll_number=username)
                )
            except User.DoesNotExist:
                return None
        else:
            return None

        if user.check_password(password):
            return user
        return None




