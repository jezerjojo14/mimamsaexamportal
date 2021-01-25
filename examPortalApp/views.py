from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json
import csv
import codecs
import random
import string
from django.contrib.auth import user_logged_in
from django.dispatch.dispatcher import receiver
from django.contrib.sessions.models import Session

from .models import User, Team, Ordering


class UserUpdateForm(forms.Form):
    passcode = forms.CharField(max_length=50, widget=forms.PasswordInput())
    file = forms.FileField(required=True)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = (request.POST["email"]).lower()
        password = request.POST["password"]
        print(password)
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            if user.check_password(password):
                if user.session_key: # check if user has session_key. This will be true for users logged in on another device
                    try:
                        s = Session.objects.get(session_key=user.session_key)
                        s.delete()
                    except Session.DoesNotExist:
                        pass
                login(request, user)
                user.session_key = request.session.session_key
                user.save()
                return HttpResponseRedirect(reverse("dashboard"))
        return render(request, "examPortalApp/index.html", {
            "message": "Invalid username and/or password."
        })
    else:
        return render(request, "examPortalApp/index.html")


#This view does two things at once
# (1) It is the one and only way to add new user and team accounts into our database
# (2) The POST method returns a JSON object of all the newest accounts along with the newly generated passwords so that the passwords could be sent to their respective email accounts
def update_accounts(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES)
        #Authenticate user trying to update the accounts and generate passwords
        if form.is_valid() and request.POST["passcode"]=="AlohomoraM1mam$aAdmin":
            print(request.FILES)
            file=request.FILES['file']
            reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
            generated_passwords={}
            print("It begins")
            for row in reader:
                team_id = row["TEAM ID"]
                print(row["SEQUENCE"])
                try:
                    team=Team.objects.create(team_id=team_id, sequence=row["SEQUENCE"], college=row["COLLEGE"], zone=row["ZONE CODE"])
                    print(team_id+" saved")
                except IntegrityError:
                    team=Team.objects.get(team_id=team_id)
                    print(team_id)
                for i in range(4):
                    if row["EMAIL ID "+str(i+1)]=="":
                        continue
                    try:
                        password=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                        user=User.objects.create_user(username=row["EMAIL ID "+str(i+1)], email=(row["EMAIL ID "+str(i+1)]).lower(), password=password, generated_pass=password)
                        if i==0:
                            user.phone_number=row["PHONE 1"]
                            user.save()
                    except IntegrityError:
                        print(row["EMAIL ID "+str(i+1)])
                        user=User.objects.get(email=(row["EMAIL ID "+str(i+1)]).lower())
                    if user.passwordSet==False:
                        generated_passwords[row["EMAIL ID "+str(i+1)]]=user.generated_pass
                    if team.users.all().filter(email=user.email).count()==0:
                        team.users.add(user, through_defaults={"order_index": i+1})
                        team.save()
            return JsonResponse(generated_passwords)
        return render(request, 'examPortalApp/update.html', {'form': form})
    else:
        form = UserUpdateForm()
        return render(request, 'examPortalApp/update.html', {'form': form})

def dashboard(request):
    if request.user.is_authenticated:
        return HttpResponse("bruh")
    else:
        return HttpResponseRedirect(reverse("index"))
