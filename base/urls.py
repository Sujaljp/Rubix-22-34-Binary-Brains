from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('items/', views.userItems, name="user-items"),
    path('delete/<str:pk>/', views.deleteItem, name="delete-item"),

    path('signup/', views.signupuser, name='signupuser'),
    path('login/', views.loginuser, name='loginuser'),
    path('logout/', views.logoutuser, name='logoutuser'),

]
