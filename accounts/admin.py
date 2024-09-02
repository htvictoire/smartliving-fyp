from django.contrib import admin
from .models import User, Favorites

admin.site.register(User)
admin.site.register(Favorites)