from django.contrib import admin

from .models import User, Team, Ordering, GlobalVariables, Question, Answer, AnswerFiles

# Register your models here.

#This means that these models can be viewed and edited by admin on the admin page

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Ordering)
admin.site.register(GlobalVariables)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerFiles)
