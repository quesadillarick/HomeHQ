from django.contrib import admin
from .models import Note, NoteCategory

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'updated_at']

admin.site.register(NoteCategory)
