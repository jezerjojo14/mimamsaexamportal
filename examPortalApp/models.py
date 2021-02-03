from django.contrib.auth.models import AbstractUser
from django.db import models

#User instances are created when registration sheets are inputted;
#They're updated when (1) sessions are created and removed, and (2) when passwords are changed
class User(AbstractUser):
    phone_number = models.CharField(max_length=15)
    #generated_pass is the initial server generated password that can be seen by us (unlike the default password field) and is initially also stored in hashed form in the default password field
    generated_pass = models.CharField(max_length=100)
    #Once the user updates their actual password from the server generated one, password_set takes the value "True". At this point no one knows their password except them
    passwordSet = models.BooleanField(default=False)
    #Session key of each user is stored. If a user tries to login again in another device (start another session), they get logged out from the former device (original session is deleted)
    session_key = models.CharField(max_length=100, null=True)

#The following two databases update when registration sheets are inputted
class Team(models.Model):
    team_id = models.CharField(max_length=15, primary_key=True)
    sequence = models.CharField(max_length=10)
    users = models.ManyToManyField(User, through="Ordering")
    college = models.CharField(max_length=200)
    zone = models.CharField(max_length=5)
    p_folder_id = models.CharField(max_length=100)
    m_folder_id = models.CharField(max_length=100)
    b_folder_id = models.CharField(max_length=100)
    c_folder_id = models.CharField(max_length=100)
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
    question_html = models.CharField(max_length=1000)
    question_subject = models.CharField(max_length=15)
