from django.shortcuts import render

def index(request):
    return render(request, "live_draft/index.html")

def room(request, room_name):
    return render(request, "live_draft/room.html", {"room_name": room_name})