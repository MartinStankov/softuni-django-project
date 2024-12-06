from django.contrib import admin

from magic_forum.notes.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('subject', 'content')
