from django.contrib import admin

from gpio.models import Pins, Board, Messages, Places

admin.site.register(Pins)
admin.site.register(Places)
admin.site.register(Board)
admin.site.register(Messages)