from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name="index"),
    path('update-accounts', views.update_accounts, name="update_accounts"),
    path('change-password', views.change_password, name="change_password"),
    path('logout', views.logout_view, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('test', views.open_test, name="test")
]
