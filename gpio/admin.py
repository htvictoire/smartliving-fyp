from django.contrib import admin

from gpio.models import Pins, Board, Places, MessageBoard
from accounts.models import Messages
admin.site.register(Pins)
admin.site.register(Places)
admin.site.register(Board)
admin.site.register(Messages)
admin.site.register(MessageBoard)