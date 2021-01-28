from django.contrib import admin

from .models import User, Team, Ordering, GlobalVariables, Question

# Register your models here.


admin.site.register(User)
admin.site.register(Team)
admin.site.register(Ordering)
admin.site.register(GlobalVariables)
admin.site.register(Question)
