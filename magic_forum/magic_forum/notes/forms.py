from django import forms

from magic_forum.notes.models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['subject', 'content']
