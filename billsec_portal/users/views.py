from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def init_admin(request):
  """Initialize admin user if no users exist."""
  if User.objects.count() == 0:
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      User.objects.create_superuser(username=username, password=password, email='')
      messages.success(request, '✅ Admin user created successfully.')
      return redirect('users:login')
    return render(request, 'init_admin.html')
  return redirect('users:login')

def login_view(request):
  """Handle user login."""
  if User.objects.count() > 0:
    if request.user.is_authenticated:
      return redirect('billing:home')

    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)

        # 🛠️ Get next page if exists, else go to home
        next_url = request.GET.get('next')
        if next_url:
          return redirect(next_url)
        return redirect('billing:home')

      else:
        messages.error(request, '❌ Invalid username or password.')

    return render(request, 'login.html')

  return redirect('users:init_admin')

@login_required
def logout_view(request):
  """Handle user logout."""
  logout(request)
  messages.success(request, '✅ You have been logged out successfully.')
  return redirect('users:login')