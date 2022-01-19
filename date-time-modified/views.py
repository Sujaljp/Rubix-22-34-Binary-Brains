import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import timedelta, date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Item


# Create your views here.
def home(request):
    return render(request, 'base/index.html')




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
    items = user.item_set.all().order_by('expirydate')
#---------------------------------------------------------------------------
  #  print("\n\n\n")

    for item in items:  # Iterating through every item
        
        item_expiry_date = item.expirydate  # fetching expiry date of each item from database
        today = date.today()    # assigning today's date to today variable
       
      #  print("Today : ",today, "\t", end="")
       
        notifiction_date =  abs(item_expiry_date - today) # Notification date is absolute difference between item_expiry_date and today
        # TODO - add notification date to database here
      #  print("Notification date : ",notifiction_date, "\n")

       ################### IF CONDITION BELOW #######################
      
      ###  if notifiction_date.days <= 3:      # Checking condition of notification
            # TODO - Create notification here
      
      #      print("Food will go bad in less 3 days") 
        
  #  print("\n\n\n")
#----------------------------------------------------------------------------
    #date = item.expirydate.date()
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


    

