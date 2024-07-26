from django.shortcuts import render
from django.http import HttpResponse

from mozilla_django_oidc.views import OIDCAuthenticationCallbackView, OIDCAuthenticationRequestView, OIDCLogoutView
from auth_app.custom import custom_get_settings


# Create your views here.
def index(request):
    return render(request, "auth_app/index.html")

def login_failure(request):    
    return render(request, "auth_app/login_status.html", context={'login_status': 'Login has failed.'})

def login_success(request):    
    return render(request, "auth_app/login_status.html", context={'login_status': 'You are logged in!'})

def logout_success(request):    
    return render(request, "auth_app/login_status.html", context={'login_status': 'You have been logged out.'})



#Override get_settings in mozilla_django_oidc views
class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    @staticmethod
    def get_settings(attr, *args) :
        return custom_get_settings(attr, *args)
        
class CustomOIDCAuthenticationRequestView(OIDCAuthenticationRequestView):
    @staticmethod
    def get_settings(attr, *args) :
        return custom_get_settings(attr, *args)
        
class CustomOIDCLogoutView(OIDCLogoutView):
    @staticmethod
    def get_settings(attr, *args) :
        return custom_get_settings(attr, *args)