from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages # Flash messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Room, Topic, Message
from .forms import RoomForm

# rooms = [
#     {'id': 1, 'name': 'Room 1'},
#     {'id': 2, 'name': 'Room 2'},
#     {'id': 3, 'name': 'Room 3'},
#     {'id': 4, 'name': 'Room 4'},
#     {'id': 5, 'name': 'Room 5'},
#     {'id': 6, 'name': 'Room 6'},
# ]


def loginPage(request):
    page = 'login'

    # For close the URL 
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('login')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred while creating')
        
    context = {'form': form}
    return render(request, 'base/login_register.html',context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Match query e.g ( q=dj => django)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ) 

    topics = Topic.objects.all()
    rooms_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': rooms_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(pk=pk)
    participants = room.participants.all()
    room_messages = room.message_set.all().order_by('-created')
    if request.method == 'POST':
        new_message = request.POST.get('body')
        Message.objects.create(room=room, user=request.user, body=new_message)
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


    context = {'room': room,'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    # For not update if you not the owner of the room
    if request.user != room.host:
        return redirect('home')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    # For not delete if you not the owner of the room
    if request.user != room.host:
        return redirect('home')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'room': room}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    # For not delete if you not the owner of the message
    if request.user != message.user:
        return redirect('home')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request, 'base/delete.html', context)