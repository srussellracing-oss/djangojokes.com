from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy
from .models import Joke


class JokeCreateView(CreateView):
    model = Joke
    fields = ['question', 'answer','category']


class JokeDetailView(DetailView):
    model = Joke


class JokeListView(ListView):
    model = Joke

class JokeUpdateView(UpdateView):
    model = Joke
    fields = ['question', 'answer','category']

class JokeDeleteView(DeleteView):
    model = Joke
    success_url = reverse_lazy('jokes:list')