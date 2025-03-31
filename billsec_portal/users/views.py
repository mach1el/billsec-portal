from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def init_admin(request):
  if User.objects.count() == 0:
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      User.objects.create_superuser(username=username, password=password, email='')
      messages.success(request, 'Admin user created successfully')
      return redirect('users:login')
    return render(request, 'init_admin.html')
  return redirect('users:login')

def login_view(request):
  if User.objects.count() > 0:
    if request.user.is_authenticated:
      return redirect('billing:home')
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect('billing:home')
      else:
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')
  return redirect('users:init_admin')

def logout_view(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
  return redirect('users:login')