from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponse # <- a class to handle sending a type of response
from .models import Artist, Song, Playlist
# This will import the class we are extending 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

# Here we will be creating a class called Home and extending it from the View class
@method_decorator(login_required, name='dispatch')
class Home(TemplateView):
    template_name = "home.html"
    # Here we have added the playlists as context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["playlists"] = Playlist.objects.all()
        return context

class About(TemplateView):
    template_name = 'about.html'

@method_decorator(login_required, name='dispatch')
class ArtistList(TemplateView):
    template_name = "artist_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name")
        if name != None:
            context["artists"] = Artist.objects.filter(name__icontains=name, user=self.request.user)
            # We add a header context that includes the search param
            context["header"] = f"Searching for {name}"
        else:
            context["artists"] = Artist.objects.filter(user=self.request.user)
            # default header for not searching 
            context["header"] = "Trending Artists"
        return context

class ArtistCreate(CreateView):
    model = Artist
    fields = ['name', 'img', 'bio', 'verified_artist']
    template_name = "artist_create.html"

    # This is our new method that will add the user into our submitted form
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArtistCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('artist_detail', kwargs={'pk': self.object.pk})

class ArtistDetail(DetailView):
    model = Artist
    template_name = "artist_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["playlists"] = Playlist.objects.all()
        return context


class ArtistUpdate(UpdateView):
    model = Artist
    fields = ['name', 'img', 'bio', 'verified_artist']
    template_name = "artist_update.html"
    success_url = "/artists/"

class ArtistDelete(DeleteView):
    model = Artist
    template_name = "artist_delete_confirmation.html"
    success_url = "/artists/"

class SongCreate(View):

    def post(self, request, pk):
        title = request.POST.get("title")
        length = request.POST.get("length")
        artist = Artist.objects.get(pk=pk)
        Song.objects.create(title=title, length=length, artist=artist)
        return redirect('artist_detail', pk=pk)

class PlaylistSongAssoc(View):

    def get(self, request, pk, song_pk):
        # get the query param from the url
        assoc = request.GET.get("assoc")
        if assoc == "remove":
            # get the playlist by the id and
            # remove from the join table the given song_id
            Playlist.objects.get(pk=pk).songs.remove(song_pk)
        if assoc == "add":
            # get the playlist by the id and
            # add to the join table the given song_id
            Playlist.objects.get(pk=pk).songs.add(song_pk)
        return redirect('home')

class Signup(View):
    # show a form to fill out
    def get(self, request):
        form = UserCreationForm()
        context = {"form": form}
        return render(request, "registration/signup.html", context)
    # on form ssubmit validate the form and login the user.
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("artist_list")
        else:
            context = {"form": form}
            return render(request, "registration/signup.html", context)
