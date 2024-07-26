from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "auth_app/index.html")

def login_failure(request):    
    return render(request, "auth_app/login_status.html", context={'login_status': 'Login has failed.'})

def login_success(request):    
    return render(request, "auth_app/login_status.html", context={'login_status': 'You are logged in!'})

def logout_success(request):    
    return render(request, "auth_app/login_status.html", context={'login_status': 'You have been logged out.'})