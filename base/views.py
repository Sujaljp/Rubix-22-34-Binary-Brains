from django.shortcuts import render, redirect
from django.contrib import messages
import datetime
import smtplib
import schedule
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Item
from django.db import IntegrityError
import requests
from foodsaver import settings
from isodate import parse_duration

def sendMail():
    item = Item.objects.all()
    today = datetime.date.today()
    for items in item:
        date= items.expirydate
        dt = datetime.timedelta(-1)
        nftdate = date+dt
        if nftdate == today:
            name = items.name
            username = items.user.username
            email = 'resqfood1@gmail.com'
            recemail = items.user.email
            password = 'Foodresq123'
            note = 'Following item will go bad by today: '+ name
            subject = 'ResQ your Items'
            msg = f'From: Food ResQ\nTo:{username}\nSubject: {subject}\n\n{note}'
            server = smtplib.SMTP('smtp.gmail.com', 587)

            server.starttls()
            server.login(email, password)
            
            server.sendmail(email, recemail, msg)
    print('Mail Sent to', recemail)


# Create your views here.
def home(request):
    #sendMail()
    schedule.every().day.at("06:00").do(sendMail)
    schedule.run_pending()
    return render(request, 'base/index.html')

def recipes(request, name):
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    search_params = {
        'part': 'snippet',
        'q': 'recipes' + name,
        'maxResults': 9,
        'type': 'video',
        'key': settings.YOUTUBE_DATA_API_KEY
    }
    video_ids = []

    r = requests.get(search_url, params=search_params)
    results = r.json()['items']
    for result in results:
        video_ids.append(result['id']['videoId'])

    video_params = {
        'part': 'snippet,contentDetails',
        'key': settings.YOUTUBE_DATA_API_KEY,
        'maxResults': 9,
        'id': ','.join(video_ids)
    }
    r = requests.get(video_url, params=video_params)
    results = r.json()['items']
    videos = []
    for result in results:

        video_data={
            'title' : result['snippet']['title'],
            'id': result['id'],
            'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
            'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60 ),
            'thumbnail': result['snippet']['thumbnails']['high']['url']
        }

        videos.append(video_data)


    context ={
        'videos':videos
    }
    return render(request, 'base/search.html', context)


# @login_required(login_url='/login')
# def recipes(request):
#     return render(request, 'base/recipes.html')




def loginuser(request):
    if request.method == 'GET':
        return render(request, 'base/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'base/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('user-items')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'base/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('user-items')
            except IntegrityError:
                return render(request, 'base/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose a new username'})
        else:
            return render(request, 'base/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

@login_required(login_url='/login')
def logoutuser(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/login')
def userItems(request):
    user = User.objects.get(id=request.user.id)
    if request.method =='POST':
        item = Item.objects.create(
            user= request.user,
            name = request.POST.get('itemname'),
            expirydate=request.POST.get('expirydate'),
        )
        date= request.POST.get('expirydate')
        year= int(date[0:4])
        month= int(date[5:7])
        day= int(date[8:])
        first = datetime.date(year, month, day)
        dt = datetime.timedelta(-1)
        ntfdate = first+dt
        print(ntfdate)
        return redirect('user-items')
    items = user.item_set.all().order_by('expirydate')

    context={'items':items}
    return render(request, 'base/items.html' , context)

@login_required(login_url='/login')
def deleteItem(request,pk):
    item = Item.objects.get(id=pk)
    if request.user != item.user:
        return HttpResponse('Not Allowed')
    if request.method == 'POST':
        item.delete()
        return redirect('user-items')
    return render(request, 'base/delete.html', {'obj':item})


    

