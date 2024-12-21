from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages # Flash messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# rooms = [
#     {'id': 1, 'name': 'Room 1'},
#     {'id': 2, 'name': 'Room 2'},
#     {'id': 3, 'name': 'Room 3'},
#     {'id': 4, 'name': 'Room 4'},
#     {'id': 5, 'name': 'Room 5'},
#     {'id': 6, 'name': 'Room 6'},
# ]


# =============== Authentication =============== #
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
    return redirect('home')

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


# =============== User Profile =============== #
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)



# =============== Home Page  =============== #
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Match query e.g ( q=dj => django)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ) 

    topics = Topic.objects.all()[0:4]
    rooms_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': rooms_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


# =============== Rooms CRUD =============== #
def room(request, pk):
    room = Room.objects.get(pk=pk)
    participants = room.participants.all()
    room_messages = room.message_set.all()
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
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form' : form,'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    # For not update if you not the owner of the room
    if request.user != room.host:
        return redirect('home')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context = {'form' : form,'topics': topics, 'room': room}
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


# =============== Messages delete =============== #
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

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html',context)

def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)