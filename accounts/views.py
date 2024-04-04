from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from .models import CustomUser
from django.contrib import messages , auth
from django.conf import settings
import requests

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            # Create a new CustomUser object and save it to the database
            user = CustomUser.objects.create_user(email=email, password=password)
            # You can perform additional actions here, such as logging the user in automatically
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')

            # Authenticate user
            user = authenticate(email=email, password=password)

            if user is not None:
                auth.login(request, user)  # Log in the user

                # Set session expiry based on remember_me checkbox
                if remember_me:
                    request.session.set_expiry(settings.SESSION_REMEMBER_ME_EXPIRY)
                else:
                    # Use default session expiry
                    request.session.set_expiry(0)

                messages.success(request, 'You are now logged in.')

                # Check for 'next' parameter in the URL
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('product_list')
            else:
                # Handle invalid credentials
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid email or password'})
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    request.session.clear()
    return redirect('login')  # Redirect to the login page after logout
