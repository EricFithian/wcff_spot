from django.contrib import admin
from .models import Artist, Playlist, Song # import the Artist model from models.py
# Register your models here.

admin.site.register(Artist) # this line will add the model to the admin panel
admin.site.register(Song) # this line will add the model to the admin panel
admin.site.register(Playlist) # this line will add the model to the admin panel