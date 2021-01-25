from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name="index"),
    path('update-accounts', views.update_accounts, name="update"),
    path('dashboard', views.dashboard, name="dashboard")
]
