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
from django.utils import timezone
import datetime
import pytz
from .models import User, Team, Ordering, GlobalVariables, Question




#  User account related views




class UserUpdateForm(forms.Form):
    passcode = forms.CharField(max_length=50, widget=forms.PasswordInput())
    file = forms.FileField(required=True)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = (request.POST["email"]).lower()
        password = request.POST["password"]
        print(password)
        if User.objects.filter(username=email).exists():
            user=User.objects.get(username=email)
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
                        user=User.objects.create_user(username=(row["EMAIL ID "+str(i+1)]).lower(), email=(row["EMAIL ID "+str(i+1)]).lower(), password=password, generated_pass=password)
                        if i==0:
                            user.phone_number=row["PHONE 1"]
                            user.save()
                    except IntegrityError:
                        print(row["EMAIL ID "+str(i+1)])
                        user=User.objects.get(email=(row["EMAIL ID "+str(i+1)]).lower())
                    if user.passwordSet==False:
                        generated_passwords[(row["EMAIL ID "+str(i+1)]).lower()]=user.generated_pass
                    if team.users.all().filter(email=user.email).count()==0:
                        team.users.add(user, through_defaults={"order_index": i+1})
                        team.save()
            return JsonResponse(generated_passwords)
        return render(request, 'examPortalApp/update.html', {'form': form})
    else:
        form = UserUpdateForm()
        return render(request, 'examPortalApp/update.html', {'form': form})

def unset_passwords(request):
    password_list={}
    for user in User.objects.all():
        if not user.passwordSet:
            password_list[user.email]=user.generated_pass
    return JsonResponse(password_list)

@login_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        email = (request.POST["email"]).lower()
        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password==confirm_password:
            if user.username==email and user.check_password(old_password):
                user.set_password(new_password)
                user.passwordSet=True
                user.save()
            elif user.username=="admin" and user.check_password(old_password): #backdoor for admin to change the password of someone else. admin has to enter his/her own password in place of old password
                try:
                    reset_user=User.objects.get(username=email)
                except:
                    return render(request, "examPortalApp/change_password.html", {
                        "message": "Email not registered"
                    })
                reset_user.set_password(new_password)
                user.passwordSet=True
                user.save()
            else:
                return render(request, "examPortalApp/change_password.html", {
                    "message": "Your credentials don't match."
                })
        else:
            return render(request, "examPortalApp/change_password.html", {
                "message": "Passwords don't match."
            })
        logout(request)
        return render(request, "examPortalApp/index.html", {
            "message": "Password successfully updated."
        })
    else:
        return render(request, "examPortalApp/change_password.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))




# Dashboard




def dashboard(request):
    if request.user.is_authenticated:
        if request.user.passwordSet:
            return render(request, "examPortalApp/dashboard.html")
        else:
            return HttpResponseRedirect(reverse("change_password"))
    else:
        return HttpResponseRedirect(reverse("index"))




# Views related to the exam portal itself



@login_required
def open_test(request):
    now = timezone.now()
    test_start=(GlobalVariables.objects.all().get_or_create(pk=1, defaults={'test_start': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 0, 0)),  'test_end': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 30, 0))})[0]).test_start
    test_end=GlobalVariables.objects.all().get(pk=1).test_end
    q_count= Question.objects.all().count();
    if now<test_start:
        return render(request, "examPortalApp/waitingroom.html", {"UTCDate": test_start.day, "UTCMonth": test_start.month, "UTCYear": test_start.year, "UTCHours": test_start.hour, "UTCMinutes": test_start.minute, "UTCSeconds": test_start.second})
    if now<test_end:
        return render(request, "examPortalApp/testportal.html", {"QCount": q_count, "UTCDate": test_end.day, "UTCMonth": test_end.month, "UTCYear": test_end.year, "UTCHours": test_end.hour, "UTCMinutes": test_end.minute, "UTCSeconds": test_end.second})
    return render(request, "examPortalApp/testended.html")

@login_required
def get_question(request, qnumber=1):
    now = timezone.now()
    test_start=(GlobalVariables.objects.all().get_or_create(pk=1, defaults={'test_start': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 0, 0)),  'test_end': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 30, 0))})[0]).test_start
    if now>test_start:
        q=Question.objects.get(question_number=qnumber)
        return JsonResponse({"content": q.question_html})
    else:
        return HttpResponse(status=403)

@login_required
def upload_answer(request, qnumber):
    pass

@login_required
def end_test(request):
    pass


    """

    DONE:

    1) Create templates for waitingroom, testportal, testended
    2) Create Question model

    TO DO:

    3) Create questionportal template
    4) Write view for post_question and delete_question
    5) Write javascript code for testportal and get_question view
    6) Write move_up and move_down views and edit questionportal accordingly

    7...) Figure out google cloud api for media


    """


# Question making portal



@login_required
def question_making_page(request, page=1):
    if request.user.username=="admin":
        q=Paginator(Question.objects.all().order_by("question_number"), 10)
        print(q.page_range)
        if page not in q.page_range:
            raise Http404
        return render(request, "examPortalApp/questionportal.html", {"questions": q.page(page), "page": page, "pagecount": q.num_pages})
    else:
        return HttpResponseRedirect(reverse("dashboard"))


@login_required
def post_question(request):
    if request.user.username=="admin":
        q=Question(question_html=(request.POST["content"]).replace("\n", "<br>"), question_number=(Question.objects.all().count()+1))
        q.save()
        return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))
    else:
        return HttpResponseRedirect(reverse("dashboard"))

@login_required
def delete_question(request):
    pass

@login_required
def edit_question(request):
    pass

@login_required
def move_to(request):
    pass

@login_required
def media_view(request):
    pass

@login_required
def upload_media(request):
    pass

@login_required
def delete_media(request):
    pass
