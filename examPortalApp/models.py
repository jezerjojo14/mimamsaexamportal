from django.contrib.auth.models import AbstractUser
from django.db import models

#User instances are created when registration sheets are inputted;
#They're updated when (1) sessions are created and removed, and (2) when passwords are changed
class User(AbstractUser):
    phone_number = models.CharField(max_length=25)
    #generated_pass is the initial server generated password that can be seen by us (unlike the default password field) and is initially also stored in hashed form in the default password field
    generated_pass = models.CharField(max_length=100)
    #Once the user updates their actual password from the server generated one, password_set takes the value "True". At this point no one knows their password except them
    passwordSet = models.BooleanField(default=False)
    #Session key of each user is stored. If a user tries to login again in another device (start another session), they get logged out from the former device (original session is deleted)
    session_key = models.CharField(max_length=100, null=True)
    # user types: participant, proctor, admin
    user_type = models.CharField(max_length=30, default='participant')

#The following two databases update when registration sheets are inputted
class Team(models.Model):
    team_id = models.CharField(max_length=15, primary_key=True)
    sequence = models.CharField(max_length=10)
    # users = models.ManyToManyField(User, through="Ordering")
    users = models.ManyToManyField(User)
    college = models.CharField(max_length=200)
    zone = models.CharField(max_length=5)
    extra_time = models.IntegerField(default=0)
    proctor_user = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL, related_name="proctored_teams")

#This database adds an extra datum to each connection between a group and its members expressing the ordering of the users in their teams
class Ordering(models.Model):
    user_instance = models.ForeignKey(User, on_delete=models.CASCADE)
    team_instance = models.ForeignKey(Team, on_delete=models.CASCADE)
    #Order index gives the users' order in the team and takes a value between 1 and 4
    order_index = models.IntegerField()

#Database containing one instance for all global variables
#Basically just using this as a list of global variables that's accessible to the admin
class GlobalVariables(models.Model):
    test_start = models.DateTimeField()
    test_end = models.DateTimeField()

class Question(models.Model):
    question_number = models.IntegerField(unique=True, null=False)
    #For MCQ, question_content takes the form '["Main question here", ["Subquestion here", ["Option A","Option B"]], ["Next subquestion", ["Option 1", "Option 2", "Option 3"]]]'
    question_content = models.TextField()
    question_subject = models.CharField(max_length=15)
    #s=subjective, m=mcq, t=train of thought
    question_type = models.CharField(max_length=2, default='s')
    question_answers = models.CharField(max_length=100, default="", blank=True)
    max_marks = models.IntegerField(default=2)

class Answer(models.Model):
    team_instance = models.ForeignKey(Team, on_delete=models.CASCADE)
    question_instance = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_content = models.TextField(default="", blank=True)
    #u=unanswered, a=answered, r=marked for review
    status = models.CharField(max_length=2, default='u')
    marks = models.FloatField(default=-1)
    graded = models.BooleanField(default=False)

class AnswerFiles(models.Model):
    answer_instance = models.ForeignKey(Answer, on_delete=models.CASCADE)
    answer_filename = models.TextField()
    page_no = models.IntegerField()

class Fishylog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    popup_opentime = models.DateTimeField()
    actionCommited = models.TextField()
    popup_closetime = models.DateTimeField(null=True, default=None)

class ChatRoom(models.Model):
    team_instance = models.ForeignKey(Team, on_delete = models.CASCADE)
    chatlog_start = models.IntegerField(default=0)

class ChatLog(models.Model):
    log_number = models.IntegerField()
    chatroom_instance = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user_instance = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
