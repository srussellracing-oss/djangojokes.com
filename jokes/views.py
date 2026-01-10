from django.db.models import Q, Avg, FloatField
from django.db.models.functions import Cast
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
import json

from .models import Joke, JokeVote
from .forms import JokeForm


class JokeCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Joke
    form_class = JokeForm
    success_message = 'Joke created.'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class JokeDeleteView(UserPassesTestMixin, DeleteView):
    model = Joke
    success_url = reverse_lazy('jokes:list')

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        return self.request.user == self.get_object().user


class JokeDetailView(DetailView):
    model = Joke


class JokeListView(ListView):
    model = Joke
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_fields, order_key, direction = self.get_order_settings()

        context['order'] = order_key
        context['direction'] = direction
        context['order_fields'] = list(order_fields.keys())[:-1]

        return context

    def get_ordering(self):
        order_fields, order_key, direction = self.get_order_settings()
        ordering = order_fields[order_key]
        return ordering if direction == 'asc' else '-' + ordering

    def get_order_settings(self):
        order_fields = self.get_order_fields()
        default_order_key = order_fields['default_key']
        order_key = self.request.GET.get('order', default_order_key)
        direction = self.request.GET.get('direction', 'desc')

        if order_key not in order_fields:
            order_key = default_order_key

        return order_fields, order_key, direction

    def get_queryset(self):
        ordering = self.get_ordering()
        qs = Joke.objects.all()

    # search filter
        if 'q' in self.request.GET:
            q = self.request.GET.get('q')
            qs = qs.filter(
            Q(question__icontains=q) | Q(answer__icontains=q)
        )

    # category/tag filter
        if 'slug' in self.kwargs:
            slug = self.kwargs['slug']
            if '/category' in self.request.path_info:
                qs = qs.filter(category__slug=slug)
            if '/tag' in self.request.path_info:
                qs = qs.filter(tags__slug=slug)

    # creator filter
        if 'username' in self.kwargs:
            username = self.kwargs['username']
            qs = qs.filter(user__username=username)

    # ⭐ ALWAYS annotate rating (renamed to avoid property conflict)
        qs = qs.annotate(
            rating_avg=Cast(Avg('jokevotes__vote'), FloatField())
    )

        return qs.prefetch_related('category').order_by(ordering)

    def get_order_fields(self):
        return {
            'joke': 'question',
            'category': 'category__category',
            'creator': 'user__username',
            'created': 'created',
            'updated': 'updated',
            'default_key': 'updated'
        }


class JokeUpdateView(SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    model = Joke
    form_class = JokeForm
    success_message = 'Joke updated.'

    def test_func(self):
        return self.request.user == self.get_object().user


def vote(request, slug):
    user = request.user
    joke = Joke.objects.get(slug=slug)
    data = json.loads(request.body)

    vote = data['vote']
    likes = data['likes']
    dislikes = data['dislikes']

    if user.is_anonymous:
        msg = 'Sorry, you have to be logged in to vote.'
    else:
        if JokeVote.objects.filter(user=user, joke=joke).exists():
            joke_vote = JokeVote.objects.get(user=user, joke=joke)

            if joke_vote.vote == vote:
                msg = 'Right. You told us already. Geez.'
            else:
                joke_vote.vote = vote
                joke_vote.save()

                if vote == -1:
                    likes -= 1
                    dislikes += 1
                    msg = "Don't like it after all, huh? OK. Noted."
                else:
                    likes += 1
                    dislikes -= 1
                    msg = 'Grown on you, has it? OK. Noted.'
        else:
            joke_vote = JokeVote(user=user, joke=joke, vote=vote)
            joke_vote.save()

            if vote == -1:
                dislikes += 1
                msg = "Sorry you didn't like the joke."
            else:
                likes += 1
                msg = "Yeah, good one, right?"

    return JsonResponse({'msg': msg, 'likes': likes, 'dislikes': dislikes})
