from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login_failure", views.login_failure, name="login_failure"),
    path("login_success", views.login_success, name="login_success"),
    path("logout_success", views.logout_success, name="logout_success")
]
