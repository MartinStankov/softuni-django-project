from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.urls import reverse_lazy
from django.contrib import messages

from magic_forum.notes.forms import NoteForm
from magic_forum.notes.models import Note


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'forum/note_list.html'
    context_object_name = 'notes'
    paginate_by = 9

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-created_at')


class NoteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Note
    template_name = 'forum/note_detail.html'

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.user


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'forum/note_form.html'
    success_url = reverse_lazy('note-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Note created successfully!')
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'forum/note_form.html'
    success_url = reverse_lazy('note-list')

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.user

    def form_valid(self, form):
        messages.success(self.request, 'Note updated successfully!')
        return super().form_valid(form)


class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = 'forum/note_confirm_delete.html'
    success_url = reverse_lazy('note-list')

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Note deleted successfully!')
        return super().delete(request, *args, **kwargs)

