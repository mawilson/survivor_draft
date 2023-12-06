from django.shortcuts import render
from django.shortcuts import redirect
from survive.forms import TeamForm
from survive.models import Team, Survivor
from django.views.generic import ListView

class HomeListView(ListView):
    """Renders the home page, with a list of all teams."""
    model = Team

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

# Create your views here.

# def home(request):
#     return render(request, "survive/home.html")

def add_team(request):
    form = TeamForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            team = form.save(commit=True)
            return redirect("home")
    else:
        return render(request, "survive/add_team.html", {"form": form})
    
def survivor(request, id):
    context = {'survivor': Survivor.objects.get(pk=id)}
    return render(request, "survive/survivor.html", context)