from django.contrib import admin

from .models import Notification, Energy
admin.site.register(Notification)
admin.site.register(Energy)