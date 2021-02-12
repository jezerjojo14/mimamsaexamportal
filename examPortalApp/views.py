

# Google Drive API

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


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

from PIL import Image
import io

import base64



#  User account related views




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
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard'))
        return render(request, "examPortalApp/index.html")

# This view does two things at once
# (1) It adds new user and team accounts into our database and creates folders in the drive where each team would upload their answers
# (2) The POST method returns a JSON object of all the newest accounts along with the newly generated passwords so that the passwords could be sent to their respective email accounts
# TODO: Make this view a background task

def update_accounts(request):
    if request.user.username=="admin":
        if request.method == 'POST':
            scope = ['https://www.googleapis.com/auth/drive']

            creds = ServiceAccountCredentials.from_json_keyfile_name('Uploaded Answers-14e35a500de2.json', scope)

            service = build('drive', 'v3', credentials=creds)

            results = service.files().list(q="name='Mimamsa Uploaded Answers 21'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                file_metadata = {
                'name': 'Mimamsa Uploaded Answers 21',
                'mimeType': 'application/vnd.google-apps.folder'
                }
                master_folder = service.files().create(body=file_metadata, fields='id').execute()
                master_folder_id=master_folder.get('id')

                permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'mimamsaportal@gmail.com',
                'sendNotificationEmails': False,
                }
                service.permissions().create(fileId=master_folder_id, body=permission).execute()

                file_metadata = {
                'name': 'Physics',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [master_folder_id],
                }
                p_folder = service.files().create(body=file_metadata, fields='id').execute()
                p_folder_id=p_folder.get('id')

                file_metadata = {
                'name': 'Chemistry',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [master_folder_id],
                }
                c_folder = service.files().create(body=file_metadata, fields='id').execute()
                c_folder_id=c_folder.get('id')

                file_metadata = {
                'name': 'Math',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [master_folder_id],
                }
                m_folder = service.files().create(body=file_metadata, fields='id').execute()
                m_folder_id=m_folder.get('id')

                file_metadata = {
                'name': 'Biology',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [master_folder_id],
                }
                b_folder = service.files().create(body=file_metadata, fields='id').execute()
                b_folder_id=b_folder.get('id')


            else:
                print(items)
                master_folder_id=items[0]['id']
            #Authenticate user trying to update the accounts and generate passwords
            file=request.FILES['file']
            if file:
                reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
                generated_passwords={}
                print("It begins")
                for row in reader:
                    team_id = row["TEAM ID"]
                    print(row["SEQUENCE"])
                    try:
                        team=Team.objects.create(team_id=team_id, sequence=row["SEQUENCE"], college=row["COLLEGE"], zone=row["ZONE CODE"])
                        file_metadata = {
                            'name': team_id,
                            'parents' : [p_folder_id],
                            'mimeType': 'application/vnd.google-apps.folder'
                        }
                        p_team_folder = service.files().create(body=file_metadata, fields='id').execute()
                        folder_id=p_team_folder.get('id')
                        team.p_folder_id=folder_id

                        file_metadata = {
                            'name': team_id,
                            'parents' : [m_folder_id],
                            'mimeType': 'application/vnd.google-apps.folder'
                        }
                        m_team_folder = service.files().create(body=file_metadata, fields='id').execute()
                        folder_id=m_team_folder.get('id')
                        team.m_folder_id=folder_id
                        file_metadata = {
                            'name': team_id,
                            'parents' : [c_folder_id],
                            'mimeType': 'application/vnd.google-apps.folder'
                        }
                        c_team_folder = service.files().create(body=file_metadata, fields='id').execute()
                        folder_id=c_team_folder.get('id')
                        team.c_folder_id=folder_id
                        file_metadata = {
                            'name': team_id,
                            'parents' : [b_folder_id],
                            'mimeType': 'application/vnd.google-apps.folder'
                        }
                        b_team_folder = service.files().create(body=file_metadata, fields='id').execute()
                        folder_id=b_team_folder.get('id')
                        team.b_folder_id=folder_id

                        team.save()
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
            return render(request, 'examPortalApp/update.html')
        else:
            return render(request, 'examPortalApp/update.html')
    else:
        return HttpResponseRedirect(reverse("dashboard"))

def unset_passwords(request):
    password_list={}
    for user in User.objects.all():
        if not user.passwordSet and user.username!="admin":
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
        if new_password==confirm_password and new_password!="":
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
            if new_password!=confirm_password:
                return render(request, "examPortalApp/change_password.html", {
                "message": "Passwords don't match."
                })
            else:
                return render(request,"examPortalApp/change_password.html", {
                "message": "Password cannot be blank."
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
        if request.user.passwordSet or request.user.username=="admin":
            return render(request, "examPortalApp/dashboard.html")
        else:
            return HttpResponseRedirect(reverse("change_password"))
    #If not logged in, redirect to login page
    else:
        return HttpResponseRedirect(reverse("index"))




# Views related to the exam portal itself



@login_required
def open_test(request):
    now = timezone.now()
    test_start=(GlobalVariables.objects.get_or_create(pk=1, defaults={'test_start': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 0, 0)),  'test_end': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 30, 0))})[0]).test_start
    test_end=GlobalVariables.objects.get(pk=1).test_end
    q_count= Question.objects.all().count();

    #If test hasn't started yet, show the waiting page,
    #If it has started but hasn't ended, show the testportal
    #If it's ended show the "Test ended" page

    if now<test_start:
        return render(request, "examPortalApp/waitingroom.html", {"UTCDate": test_start.day, "UTCMonth": test_start.month, "UTCYear": test_start.year, "UTCHours": test_start.hour, "UTCMinutes": test_start.minute, "UTCSeconds": test_start.second})
    if now<test_end:
        return render(request, "examPortalApp/testportal.html", {"QCount": q_count, "UTCDate": test_end.day, "UTCMonth": test_end.month, "UTCYear": test_end.year, "UTCHours": test_end.hour, "UTCMinutes": test_end.minute, "UTCSeconds": test_end.second})
    return render(request, "examPortalApp/testended.html")

@login_required
def get_question(request, qnumber=1):
    now = timezone.now()
    test_start=(GlobalVariables.objects.get_or_create(pk=1, defaults={'test_start': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 0, 0)),  'test_end': pytz.UTC.localize(datetime.datetime(2021, 1, 26, 22, 30, 0))})[0]).test_start
    if now>test_start:
        q=Question.objects.get(question_number=qnumber)
        return JsonResponse({"content": q.question_html})
    else:
        return HttpResponse(status=403)

@login_required
def get_answers(request, qnumber):
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('Uploaded Answers-14e35a500de2.json', scope)
    service = build('drive', 'v3', credentials=creds)

    team=request.user.team_set.first()

    q=Question.objects.get(question_number=int(qnumber))
    subject=q.question_subject

    #Get the team folder corresponding to the subject

    if subject=="Physics":
        folder_id = team.p_folder_id
    if subject=="Math":
        folder_id = team.m_folder_id
    if subject=="Biology":
        folder_id = team.b_folder_id
    if subject=="Chemistry":
        folder_id = team.c_folder_id

    #Get a folder for the question

    results = service.files().list(q="name='Question "+str(qnumber)+"' and '"+folder_id+"' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    #If it doesn't exist, return an empty list to show that there aren't any uploaded answers yet

    if not items:
        return JsonResponse({"images":[]})

    #This is the folder named "Question N" in the folder named after the team id, which in turn is in the folder named after the subject
    subfolder_id=items[0]['id']

    results = service.files().list(q="'"+subfolder_id+"' in parents", pageSize=30, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    images=[]

    #Get all the images and generate a data blob URI for each of them

    for item in items:
        file_id=item['id']
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()

        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        # Download the data in chunks
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)

        prefix = 'data:image/jpeg;base64,'
        contents=fh.read()
        data_url = prefix + str((base64.b64encode(contents)).decode('ascii'))
        images+=[data_url]

    #Pass the list of data blob text in a JSON response
    return JsonResponse({"images":images})

@login_required
def upload_answer(request):
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('Uploaded Answers-14e35a500de2.json', scope)
    service = build('drive', 'v3', credentials=creds)

    user=request.user
    team=user.team_set.first()
    print(request.POST)
    answerfile=request.FILES["file"]
    qnumber=request.POST["qnumber"]
    try:
        q=Question.objects.get(question_number=int(qnumber))
    except:
        print(qnumber)
        raise Http404;
    subject=q.question_subject

    #Resize and compress uploaded image

    im = Image.open(answerfile)
    w, h = im.size
    f=(250000/(w*h))**(0.5)

    im=im.resize((int(w*f), int(h*f)))
    rgb_im = im.convert("RGB")

    b = io.BytesIO()
    rgb_im.save(b, "JPEG", optimize=True, quality=70)
    b.seek(0)

    #Find the team folder under the respective subject folder

    if subject=="Physics":
        folder_id = team.p_folder_id
    if subject=="Math":
        folder_id = team.m_folder_id
    if subject=="Biology":
        folder_id = team.b_folder_id
    if subject=="Chemistry":
        folder_id = team.c_folder_id

    #Get or create a folder for the question

    results = service.files().list(q="name='Question "+str(qnumber)+"' and '"+folder_id+"' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        subfolder_metadata = {
            'name': 'Question '+str(qnumber),
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        subfolder = service.files().create(body=subfolder_metadata, fields='id').execute()
        subfolder_id=subfolder.get('id')

    else:
        print(items)
        subfolder_id=items[0]['id']

    #Count the number of files in this folder

    results = service.files().list(q="'"+subfolder_id+"' in parents", pageSize=30, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    count=len(items)

    #The image file to be uploaded would be named the number 0 if it's the first upload, 1 if it's the second, and so on

    file_metadata = {
        'name': str(count),
        'parents': [subfolder_id]
    }
    media = MediaIoBaseUpload(b,
                            mimetype='image/jpeg',
                            resumable=True)
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()

    #Reloads the page. Hopefully can be avoided using JS fetch API
    return HttpResponseRedirect(reverse("test"))


# TODO:
@login_required
def end_test(request):
    pass



# Question making portal



@login_required
def question_making_page(request, page=1):
    if request.user.username=="admin":
        q=Paginator(Question.objects.all().order_by("question_number"), 10)
        if page not in q.page_range:
            raise Http404
        return render(request, "examPortalApp/questionportal.html", {"questions": q.page(page), "page": page, "pagecount": q.num_pages})
    #If not logged in as admin, redirect to dashboard
    else:
        return HttpResponseRedirect(reverse("dashboard"))


@login_required
def post_question(request):
    if request.user.username=="admin":
        q=Question(question_html=(request.POST["content"]).replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>"), question_number=(Question.objects.all().count()+1), question_subject=request.POST["subject"])
        q.save()
        #Redirect to page 1 of the question making portal
        return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))
    else:
        return HttpResponseRedirect(reverse("dashboard"))



# TODO:
@login_required
def delete_question(request):
    if request.user.username=="admin":
        print(request.body)
        post_data = json.loads(request.body.decode("utf-8"))
        q=Question.objects.get(id=post_data["id"])
        print(q.question_html)
        total=Question.objects.all().count()
        qnum=q.question_number
        q.delete()
        for i in range(total-qnum):
            m=Question.objects.get(question_number=qnum+(i+1))
            m.question_number-=1
            m.save()
        print("--------------")
        print(('{"content":"')+(q.question_html)+('", "subject":"'+q.question_subject+'"}'))
        return HttpResponse(status=201)

@login_required
def edit_question(request):
    subjects=["Physics", "Biology", "Math", "Chemistry"]
    if request.user.username=="admin":
        print(request.POST)
        q=Question.objects.get(id=int(request.POST["id"]))
        print(q.question_html)
        q.question_html=(request.POST["content"]).replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
        if request.POST["subject"] in subjects:
            q.question_subject=request.POST["subject"]
        qnumber=int(request.POST["qnumber"])
        total=Question.objects.all().count()
        if qnumber<1:
            qnumber=1
        elif qnumber>total:
            qnumber=total
        old_qnum=q.question_number
        if qnumber>old_qnum:
            q.question_number=total+1
            q.save()
            for i in range(qnumber-old_qnum):
                m=Question.objects.get(question_number=old_qnum+(i+1))
                m.question_number-=1
                m.save()
            q.question_number=qnumber
        elif qnumber<old_qnum:
            q.question_number=total+1
            q.save()
            for i in range(old_qnum-qnumber):
                m=Question.objects.get(question_number=old_qnum-(i+1))
                m.question_number+=1
                m.save()
            q.question_number=qnumber
        q.save()
        print("--------------")
        print(('{"content":"')+(q.question_html)+('", "subject":"'+q.question_subject+'"}'))
        return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))
        # return HttpResponse(('{"content":"')+(q.question_html)+('", "subject":"'+q.question_subject+'"}'), status=201)
    # else:
    #     return HttpResponse(status=403)

# TODO:
@login_required
def move_to(request):
    pass

# TODO:
@login_required
def media_view(request):
    pass

# TODO:
@login_required
def upload_media(request):
    pass

# TODO:
@login_required
def delete_media(request):
    pass




# def drive_clear(request):
#
#     scope = ['https://www.googleapis.com/auth/drive']
#
#     creds = ServiceAccountCredentials.from_json_keyfile_name('Uploaded Answers-14e35a500de2.json', scope)
#
#     service = build('drive', 'v3', credentials=creds)
#
#     # Call the Drive v3 API
#     results = service.files().list(
#         pageSize=60, fields="nextPageToken, files(id, name)").execute()
#     items = results.get('files', [])
#
#     if not items:
#         print('No files found.')
#     else:
#         print('Files:')
#         for item in items:
#             print(u'{0} ({1})'.format(item['name'], item['id']))
#             service.files().delete(fileId=item['id']).execute()
#
#     return HttpResponse("Drive cleared")

# def drive_list(request):
#
#     scope = ['https://www.googleapis.com/auth/drive']
#
#     creds = ServiceAccountCredentials.from_json_keyfile_name('Uploaded Answers-14e35a500de2.json', scope)
#
#     service = build('drive', 'v3', credentials=creds)
#
#     # Call the Drive v3 API
#     results = service.files().list(
#         pageSize=60, fields="nextPageToken, files(id, name)").execute()
#     items = results.get('files', [])
#
#     if not items:
#         print('No files found.')
#     else:
#         print('Files:')
#         for item in items:
#             print(u'{0} ({1})'.format(item['name'], item['id']))
#
#     return HttpResponse("Woohoo!")
