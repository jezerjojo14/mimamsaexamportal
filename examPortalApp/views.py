# S3 API

import boto3
from botocore.exceptions import ClientError
import botocore
from boto3.s3.transfer import TransferConfig



import os.path
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
import ast
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

from .models import User, Team, Ordering, GlobalVariables, Question, Answer, AnswerFiles

from PIL import Image
import io

import base64
from threading import *

from django.contrib import messages

GB = 1024 ** 3
config = TransferConfig(multipart_threshold=0.1*GB)

# def db_test(request):
#     # user=User.objects.get(username='starforce30@gmail.com')
#     # team=user.team_set.first()
#     team=Team.objects.get(sequence="10584")
#     l=list(team.users.values_list('username', 'generated_pass'))
#     print(team)
#     print(l)
#     return HttpResponse('yee')


def csrf_failure(request, reason=""):
    return render(request, "500.html")

def password_list(request):
    if request.user.username=="admin":
        users=User.objects.filter(passwordSet=False)
        d={}
        for user in users:
            d[user.username]=user.generated_pass
        return JsonResponse(d)

def mail_change(request):
    if request.user.username=="admin":
        if request.method == "POST":
            sequence = (request.POST["sequence"]).lower()
            order_index = int(request.POST["order_index"])
            new_email = (request.POST["new_email"]).lower()
            user=User.objects.get(team__sequence=sequence, ordering__order_index=order_index)
            old_email=user.username
            user.username=new_email
            user.email=new_email
            user.save()
            return render(request, "examPortalApp/index0.html", {
                "message": old_email+" to "+user.username
            })
        else:
            return render(request, "examPortalApp/index0.html")


#  User account related views


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = (request.POST["email"]).lower()
        password = request.POST["password"]
        if User.objects.filter(username=email).exists():
            user=User.objects.get(username=email)
            if user.check_password(password):
                if user.session_key and user.username!='admin' and user.username!='jezer': # check if user has session_key. This will be true for users logged in on another device
                    try:
                        s = Session.objects.get(session_key=user.session_key)
                        s.delete()
                    except Session.DoesNotExist:
                        pass
                login(request, user)
                user.session_key = request.session.session_key
                user.save()
                return HttpResponseRedirect(reverse("dashboard"))
            else:
                return render(request, "examPortalApp/index.html", {
                    "message": "Incorrect password."
                })
        else:
            return render(request, "examPortalApp/index.html", {
                "message": "Username does not exist."
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
    class GeneratePass(Thread):
        def run(self):
            file=request.FILES['file']
            if file:
                reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
                generated_passwords={}
                print("It begins")
                for row in reader:
                    team_id = row["Code"]
                    print(row["Code"])
                    try:
                        team=Team.objects.create(team_id=team_id, sequence=row["Code of Team"], college=row["Name Of College"], zone=row["Zone Code of your College (Zone)"])
                        team.save()
                        print(team_id+" saved")
                    except IntegrityError:
                        team=Team.objects.get(team_id=team_id)
                        print(team_id)
                    for i in range(4):
                        if row["Email of Participant "+str(i+1)]=="":
                            continue
                        try:
                            password=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                            user=User.objects.create_user(username=(row["Email of Participant "+str(i+1)]).lower(), email=(row["Email of Participant "+str(i+1)]).lower(), password=password, generated_pass=password, phone_number=row["Phone Number of Participant "+str(i+1)])
                        except IntegrityError:
                            print(row["Email of Participant "+str(i+1)])
                            user=User.objects.get(email=(row["Email of Participant "+str(i+1)]).lower())
                        if user.passwordSet==False:
                            generated_passwords[(row["Email of Participant "+str(i+1)]).lower()]=user.generated_pass
                        if team.users.all().filter(email=user.email).count()==0:
                            team.users.add(user)
                            ordering=Ordering.objects.create(team_instance=team, user_instance=user, order_index=i+1)
                            ordering.save()
                            team.save()
                return JsonResponse(generated_passwords)
            print("Accounts updated")
    if request.user.username=="admin":
        if request.method=="POST":
            #Authenticate user trying to update the accounts and generate passwords
            thread1 = GeneratePass()
            thread1.start()
            return render(request,"examPortalApp/updateconfirmation.html",{'confirmvar':'Updates initiated'})
        else:
            return render(request,"examPortalApp/update.html")
    else:
        return HttpResponseRedirect(reverse("dashboard"))

def unset_passwords(request):
    password_list={}
    for user in User.objects.all():
        if not user.passwordSet and user.username!="admin":
            password_list[user.email]=user.generated_pass
    return JsonResponse(password_list)

@login_required(login_url='/')
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
                reset_user.passwordSet=True
                reset_user.save()
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




# Misc




def dashboard(request):
    if request.user.is_authenticated:
        if request.user.passwordSet or request.user.username=="admin":
            team=request.user.team_set.first()
            return render(request, "examPortalApp/dashboard.html", {"team": team})
        else:
            return HttpResponseRedirect(reverse("change_password"))
    #If not logged in, redirect to login page
    else:
        return HttpResponseRedirect(reverse("index"))

def instructions(request):
    try:
        team=request.user.team_set.first()
    except:
        return render(request, "examPortalApp/instructions.html")
    return render(request, "examPortalApp/instructions.html", {"team": team})




# Views related to the exam portal itself



@login_required(login_url='/')
def open_test(request, qnumber=None, message=""):
    now = timezone.now()
    test_start=(GlobalVariables.objects.get_or_create(pk=1, defaults={'test_start': pytz.UTC.localize(datetime.datetime(2021, 4, 18, 4, 30, 0)),  'test_end': pytz.UTC.localize(datetime.datetime(2021, 4, 18, 6, 30, 0))})[0]).test_start
    team=request.user.team_set.first()
    test_start += datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    #If test hasn't started yet, show the waiting page,
    #If it has started but hasn't ended, show the testportal
    #If it's ended show the "Test ended" page

    if now<test_start:
        template_var= {
            "UTCDate": test_start.day,
            "UTCMonth": test_start.month,
            "UTCYear": test_start.year,
            "UTCHours": test_start.hour,
            "UTCMinutes": test_start.minute,
            "UTCSeconds": test_start.second
        }
        template_var["team"]=team
        return render(request, "examPortalApp/waitingroom.html", template_var)

    if now>test_end:
        return render(request, "examPortalApp/testended.html")

    q_count= Question.objects.all().count();
    q_current = 1 if (qnumber is None) else int(qnumber);
    try:
        q=Question.objects.get(question_number=qnumber)
    except:
        raise Http404

    template_var= {
        "UTCDate": test_end.day,
        "UTCMonth": test_end.month,
        "UTCYear": test_end.year,
        "UTCHours": test_end.hour,
        "UTCMinutes": test_end.minute,
        "UTCSeconds": test_end.second
    }

    review_questions=list(Question.objects.filter(answer__team_instance=team, answer__status='r').values_list('question_number', flat=True))
    answered_questions=list(Question.objects.filter(answer__team_instance=team, answer__status='a').values_list('question_number', flat=True))

    while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
        Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
    a=(Answer.objects.get_or_create(question_instance=q, team_instance=team))[0]

    template_var["review_questions"]=review_questions
    template_var["answered_questions"]=answered_questions
    template_var["answer_status"]=a.status
    template_var["team"]=team
    template_var["QNum"]=q_current
    template_var["QCount"]=q_count


    if q.question_type=='s':
        uploaded_files=list(AnswerFiles.objects.filter(answer_instance=a).order_by('page_no').values_list('answer_filename', flat=True))

        template_var["QType"]='s'
        template_var["content"]=q.question_content
        template_var["labels"]=[]
        template_var["options"]=[]
        template_var["selected_options"]=[]
        template_var["uploaded_files"]=uploaded_files
        template_var["answer_text"]=a.answer_content
        template_var["answer_text_empty"]=(len(a.answer_content.strip())==0)


        return render(request, "examPortalApp/testportal.html", template_var)

    if q.question_type=='m':
        if a.answer_content=="":
            a.answer_content=str([])
            a.save()
        selected_options=ast.literal_eval(a.answer_content)
        content=ast.literal_eval(q.question_content)
        setup=content[0]
        option_sets=[]
        labels=[]
        i=1
        while i<len(content):
            #option_sets=[["label1", "opt1_1", "opt2_1", "opt3_1", "opt4_1"], ["label2", "opt1_2", "opt2_2", "opt3_2", "opt4_2"]]
            option_sets+=[[content[i][0]]+content[i][1]]
            i+=1

        template_var["QType"]='m'
        template_var["content"]=setup
        template_var["labels"]=labels
        template_var["options"]=option_sets
        template_var["selected_options"]=selected_options
        template_var["uploaded_files"]=[]
        template_var["answer_text"]=""
        template_var["answer_text_empty"]=True

        return render(request, "examPortalApp/testportal.html", template_var)

    if q.question_type=='t':
        uploaded_files=list(AnswerFiles.objects.filter(answer_instance = a).order_by('page_no').values_list('answer_filename', flat=True))
        if a.answer_content=="":
            a.answer_content=str([[], ""])
            a.save()
        selected_option=(ast.literal_eval(a.answer_content))[0]
        content=ast.literal_eval(q.question_content)
        setup=content[0]
        options=content[1]

        template_var["QType"]='t'
        template_var["content"]=setup
        template_var["labels"]=[]
        template_var["options"]=options
        template_var["selected_options"]=selected_option
        template_var["uploaded_files"]=uploaded_files
        template_var["answer_text"]=(ast.literal_eval(a.answer_content))[1]
        template_var["answer_text_empty"]=(len((ast.literal_eval(a.answer_content))[1].strip())==0)

        return render(request, "examPortalApp/testportal.html", template_var)


@login_required(login_url='/')
def get_answer(request, page_no, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    if now<test_end and now>test_start:

        q=Question.objects.get(question_number=int(qnumber))
        subject=q.question_subject
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get(team_instance=team, question_instance=q)
        af=AnswerFiles.objects.get(answer_instance=a, page_no=page_no)

        s3 = boto3.client("s3")
        response = s3.list_objects_v2(
                Bucket='mimamsauploadedanswers',
                Prefix =subject+'/Q'+str(q.id)+'/'+team.team_id+'/'+af.answer_filename+'.jpeg',
                MaxKeys=100 )

        image=""

        if "Contents" in response:
            fh = io.BytesIO()

            # Initialise a downloader object to download the file
            s3.download_fileobj('mimamsauploadedanswers', subject+'/Q'+str(q.id)+'/'+team.team_id+'/'+af.answer_filename+'.jpeg', fh)
            fh.seek(0)

            prefix = 'data:image/jpeg;base64,'
            contents=fh.read()
            image = prefix + str((base64.b64encode(contents)).decode('ascii'))
        else:
            af.delete()

        return JsonResponse({"image":image})
    else:
        raise Http404;

@login_required(login_url='/')
def del_answer(request, page_no, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time + 10)

    if now<test_end and now>test_start:

        q=Question.objects.get(question_number=int(qnumber))
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get(team_instance=team, question_instance=q)

        subject=q.question_subject

        s3 = boto3.client("s3")
        response = s3.list_objects_v2(
                Bucket='mimamsauploadedanswers',
                Prefix =subject+'/Q'+str(q.id)+'/'+team.team_id,
                MaxKeys=100 )


        if "Contents" in response and page_no<len(response["Contents"]):
            af=AnswerFiles.objects.get(answer_instance=a, page_no=page_no)
            filename=af.answer_filename
            noofpages = AnswerFiles.objects.filter(answer_instance = a).count()

            s3.delete_object(Bucket='mimamsauploadedanswers', Key=subject+'/Q'+str(q.id)+'/'+team.team_id+'/'+filename+'.jpeg')
            af.delete()

            #noofpages=5
            #page_no=2

            # 0 1 2 3 4  ->  0 1 3 4
            # no of iterations needed = 2 = noofpages-page_no-1
            #First iteration: get instance with page_no 3 = page_no+i+1

            for i in range(noofpages-page_no-1):
                af=AnswerFiles.objects.get(answer_instance=a, page_no=page_no+i+1)
                af.page_no=page_no+i
                af.save()

            noofpages = AnswerFiles.objects.filter(answer_instance = a).count()

            if noofpages==0 and a.status=='a':
                a.status='u'
                a.save()

            return HttpResponse(status=201)

        return HttpResponse(status=404)
    else:
        raise Http404;


@login_required(login_url='/')
def move_up(request):

    post_data = json.loads(request.body.decode("utf-8"))

    qnumber=post_data["qnumber"]
    page_no=int(post_data["page_no"])

    team=request.user.team_set.first()

    q=Question.objects.get(question_number=int(qnumber))
    a=Answer.objects.get(team_instance=team, question_instance=q)

    subject=q.question_subject

    af1=AnswerFiles.objects.get(answer_instance=a, page_no=page_no)
    try:
        af2=AnswerFiles.objects.get(answer_instance=a, page_no=page_no-1)
    except Exception as e:
        print(e)

    t=af1.page_no
    af1.page_no=af2.page_no
    af2.page_no=t
    af1.save()
    af2.save()

    return HttpResponse(status="201")


@login_required(login_url='/')
def move_down(request):

    post_data = json.loads(request.body.decode("utf-8"))

    qnumber=post_data["qnumber"]
    page_no=int(post_data["page_no"])

    team=request.user.team_set.first()

    q=Question.objects.get(question_number=int(qnumber))
    a=Answer.objects.get(team_instance=team, question_instance=q)

    subject=q.question_subject

    try:
        af1=AnswerFiles.objects.get(answer_instance=a, page_no=page_no)
        af2=AnswerFiles.objects.get(answer_instance=a, page_no=page_no+1)
    except:
        print("oops")

    t=af1.page_no
    af1.page_no=af2.page_no
    af2.page_no=t
    af1.save()
    af2.save()

    return HttpResponse(status="201")



@login_required(login_url='/')
def get_m_answers(request, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    if now<test_end and now>test_start:
        q=Question.objects.get(question_number=int(qnumber))
        try:
            a=Answer.objects.get(team_instance=team, question_instance=q)
            return JsonResponse({"answers":ast.literal_eval(a.answer_content)})
        except:
            return JsonResponse({"answers": []})
    else:
        raise Http404;


@login_required(login_url='/')
def get_t_answers(request, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    if now<test_end and now>test_start:
        q=Question.objects.get(question_number=int(qnumber))
        try:
            a=Answer.objects.get(team_instance=team, question_instance=q)
            l=ast.literal_eval(a.answer_content)
            if len(l)==1:
                return JsonResponse({"choice":l[0][0], "text": ""})
            else:
                return JsonResponse({"choice":l[0][0], "text": l[1]})
        except:
            return JsonResponse({"choice":-1, "images": [], "text": ""})
    else:
        raise Http404;


@login_required(login_url='/')
def submit_MCQ(request):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time + 10)

    if now<test_end and now>test_start:
        qnumber=request.POST["qnumber"]
        q=Question.objects.get(question_number=qnumber)
        countPlus1=len(ast.literal_eval(q.question_content))
        answer=[]
        i=1
        while i < countPlus1:
            if "choice-"+str(i) in request.POST:
                answer+=[int(request.POST["choice-"+str(i)])]
            i+=1

        a=(Answer.objects.get_or_create(question_instance=q, team_instance=team))[0]
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a.answer_content=str(answer)
        if len(answer)==len(ast.literal_eval(q.question_content))-1:
            a.status='a'
        elif a.status=='a':
            a.status='u'
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;

#This function is for saving the choice, not the explanation. The latter is handled by upload_answer/upload_text_answer
@login_required(login_url='/')
def submit_TT(request):
    team=request.user.team_set.first()
    now = timezone.now()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time + 10)

    if now<test_end and now>test_start:
        i=1
        answer=[[], ""]
        if "choice" in request.POST:
            answer[0]=[int(request.POST["choice"])]
        q=Question.objects.get(question_number=request.POST["qnumber"])
        qnumber=request.POST["qnumber"]

        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]
        if a.answer_content!="":
            answer[1]=(ast.literal_eval(a.answer_content))[1]
        if len(answer[0])==0 and a.status=='a':
            a.status='u'
        a.answer_content=str(answer)
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;

@login_required(login_url='/')
def upload_text_answer(request):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time + 10)

    if now<test_end and now>test_start:
        q=Question.objects.get(question_number=request.POST["qnumber"])
        qnumber=request.POST["qnumber"]
        subject=q.question_subject

        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]

        s3 = boto3.resource('s3')
        bucket = s3.Bucket('mimamsauploadedanswers')
        bucket.objects.filter(Prefix=subject+'/Q'+str(q.id)+'/'+team.team_id).delete()

        AnswerFiles.objects.filter(answer_instance = a).delete()

        if request.POST["answer_text"].strip() == "" and a.status=='a':
            a.status='u'

        if q.question_type=='s':
            a.answer_content=request.POST["answer_text"].strip()
        elif q.question_type=='t':
            a.answer_content=str([(ast.literal_eval(a.answer_content))[0], request.POST["answer_text"].strip()])
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;


@login_required(login_url='/')
def upload_answer(request):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time + 10)

    if now<test_end and now>test_start:
        answerfile=request.FILES["file"]
        qnumber=request.POST["qnumber"]
        try:
            q=Question.objects.get(question_number=int(qnumber))
            while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
                Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
            a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]
        except:
            print(qnumber)
            raise Http404;
        subject=q.question_subject

        if q.question_type=='s':
            a.answer_content=""
        elif q.question_type=='t':
            a.answer_content=[(ast.literal_eval(a.answer_content))[0], ""]
        a.save()

        if team is None:
            return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
        #Resize and compress uploaded image

        try:
            im = Image.open(answerfile)
            im.verify()
        except:
            #manage exceptions here
            messages.info(request, 'Image file corrupt or unsupported')
            return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
        # im.seek(0)
        im = Image.open(answerfile)
        w, h = im.size
        f=(250000/(w*h))**(0.5)

        im=im.resize((int(w*f), int(h*f)))
        rgb_im = im.convert("RGB")

        b = io.BytesIO()
        rgb_im.save(b, "JPEG", optimize=True, quality=70)
        b.seek(0)

        s3 = boto3.resource('s3')
        bucket = s3.Bucket('mimamsauploadedanswers')
        suff=0
        fn=os.path.basename(answerfile.name)
        key = fn[0:fn.find(".")]+str(suff)

        exists=True

        while exists:
            try:
                s3.Object('mimamsauploadedanswers', subject+'/Q'+str(q.id)+'/'+team.team_id+'/'+key+".jpeg").load()
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    # The object does not exist.
                    exists=False
                else:
                    # Something else has gone wrong.
                    raise
            else:
                # The object does exist.
                suff+=1
                key = fn[0:fn.find(".")]+str(suff)


        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        ansinst = Answer.objects.get_or_create(team_instance = team, question_instance = q)
        ansinst[0].save()

        bucket.upload_fileobj(b, subject+'/Q'+str(q.id)+'/'+team.team_id+'/'+key+'.jpeg', Config=config)

        noofpages = AnswerFiles.objects.filter(answer_instance = (ansinst[0])).count()
        af = AnswerFiles.objects.create(answer_instance=ansinst[0], answer_filename=key, page_no = noofpages)
        af.save()

        if AnswerFiles.objects.filter(answer_instance=ansinst[0], page_no = noofpages).count()>1:
            af.page_no+=1
            af.save()

        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;



@login_required(login_url='/')
def mark_for_review(request, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    if now<test_end and now>test_start:
        user=request.user
        team=request.user.team_set.first()
        q=Question.objects.get(question_number=int(qnumber))
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]
        a.status='r'
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;

@login_required(login_url='/')
def mark_as_answered(request, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    if now<test_end and now>test_start:
        user=request.user
        team=user.team_set.first()
        q=Question.objects.get(question_number=int(qnumber))
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]
        a.status='a'
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;

@login_required(login_url='/')
def mark_as_unanswered(request, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time)

    if now<test_end and now>test_start:
        user=request.user
        q=Question.objects.get(question_number=int(qnumber))
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]
        a.status='u'
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;


@login_required(login_url='/')
def clear_t_options(request, qnumber):
    now = timezone.now()
    team=request.user.team_set.first()
    test_start=GlobalVariables.objects.get(pk=1).test_start + datetime.timedelta(seconds=team.extra_time)
    test_end=GlobalVariables.objects.get(pk=1).test_end + datetime.timedelta(seconds=team.extra_time + 10)

    if now<test_end and now>test_start:
        user=request.user
        team=user.team_set.first()
        q=Question.objects.get(question_number=int(qnumber))
        while Answer.objects.filter(question_instance=q, team_instance=team).count()>1:
            Answer.objects.filter(question_instance=q, team_instance=team).first().delete()
        a=Answer.objects.get_or_create(question_instance=q, team_instance=team)[0]
        a.answer_content=str([[], (ast.literal_eval(a.answer_content))[1]])
        if a.status=='a':
            a.status='u';
        a.save()
        return HttpResponseRedirect(reverse("test_no", kwargs={"qnumber":str(qnumber)}))
    else:
        raise Http404;




# Question making portal




@login_required(login_url='/')
def question_making_page(request, page=1):
    if request.user.username=="admin":
        q=Paginator(Question.objects.all().order_by("question_number"), 10)
        QCount=Question.objects.all().count()
        if page not in q.page_range:
            raise Http404
        return render(request, "examPortalApp/questionportal.html", {"QCount": QCount, "questions": q.page(page), "page": page, "pagecount": q.num_pages})
    #If not logged in as admin, redirect to dashboard
    else:
        return HttpResponseRedirect(reverse("dashboard"))


@login_required(login_url='/')
def post_question(request):
    if request.user.username=="admin":
        if request.POST["qtype"]=='s':
            q=Question(question_content=((request.POST["content"]).replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")).strip(), question_number=(Question.objects.all().count()+1), question_subject=request.POST["subject"], question_type='s', question_answers='')
            q.save()
            #Redirect to page 1 of the question making portal
            return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))
        if request.POST["qtype"]=='m':
            answers=[]
            content=[((request.POST["content"]).replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")).strip()]
            i=1
            while "opt-"+str(i) in request.POST:
                if (i-1)%4==0:
                    content+=[[request.POST["mcq-set-"+str(int((i-1)/4))+"-label"], []]]
                content[1+int((i-1)/4)][1]+=[request.POST["opt-"+str(i)]]
                if "correct_"+str(i) in request.POST:
                    answers+=[i]
                i+=1
            q=Question(question_content=str(content), question_number=(Question.objects.all().count()+1), question_subject=request.POST["subject"], question_type='m', question_answers=str(answers))
            q.save()
            return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))
        if request.POST["qtype"]=='t':
            answers=[]
            content=[((request.POST["content"]).replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")).strip(), []]
            i=1
            while "opt-"+str(i) in request.POST:
                content[1]+=[request.POST["opt-"+str(i)]]
                if "correct_"+str(i) in request.POST:
                    answers+=[i]
                i+=1
            q=Question(question_content=str(content), question_number=(Question.objects.all().count()+1), question_subject=request.POST["subject"], question_type='t', question_answers=str(answers))
            q.save()
            return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))

    else:
        return HttpResponseRedirect(reverse("dashboard"))



@login_required(login_url='/')
def delete_question(request):
    if request.user.username=="admin":
        post_data = json.loads(request.body.decode("utf-8"))
        q=Question.objects.get(id=post_data["id"])
        total=Question.objects.all().count()
        qnum=q.question_number
        q.delete()
        for i in range(total-qnum):
            m=Question.objects.get(question_number=qnum+(i+1))
            m.question_number-=1
            m.save()
        return HttpResponse(status=201)

@login_required(login_url='/')
def edit_question(request):
    subjects=["Physics", "Biology", "Math", "Chemistry"]
    if request.user.username=="admin":
        q=Question.objects.get(id=int(request.POST["id"]))
        q.question_content=(request.POST["content"]).replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
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
        return HttpResponseRedirect(reverse("questionportal", kwargs={'page':1}))

def loader(request):
    return HttpResponse("loaderio-bc4611489ba175954b1027ee937bd232")




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
