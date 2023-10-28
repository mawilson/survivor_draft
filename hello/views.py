from typing import Any
from django.shortcuts import render
from django.http import HttpResponse
import re
from django.utils.timezone import datetime

from django.shortcuts import redirect
from hello.forms import LogMessageForm
from hello.models import LogMessage

from django.views.generic import ListView

# Create your views here.

# def home(request):
#     #return HttpResponse("Hello, Django!")
#     return render(request, "hello/home.html")

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

def about(request):
    return render(request, "hello/about.html")

def contact(request):
    return render(request, "hello/contact.html")

# code version using no templates
# def hello_there(request, name):
#     now = datetime.now()
#     formatted_now = now.strftime("%a, %d %b, %y at %X")

#     # Filter the name argument to letters only using regular expressions. URL arguments
#     # can contain arbitrary text, so we restrict to safe characters only.
#     match_object = re.match("[a-zA-z]+", name)

#     if match_object:
#         clean_name = match_object.group(0)
#     else:
#         clean_name = "FrIeND"

#     content = "Hello there, " + clean_name + "! It's " + formatted_now

#     return HttpResponse(content)

def hello_there(request, name):
    print(request.build_absolute_uri()) # optional
    return render(
        request,
        'hello/hello_there.html',
        {
            'name': name,
            'date': datetime.now()
        }
    )

def log_message(request):
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    else:
        return render(request, "hello/log_message.html", {"form": form}) # GET case, display form