from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name="index"),
    path('update-accounts', views.update_accounts, name="update_accounts"),
    path('change-password', views.change_password, name="change_password"),
    path('logout', views.logout_view, name="logout"),
    path('unset-passwords', views.unset_passwords, name="unset_passwords"),  #"unset" is an adjective here, not a verb

    path('dashboard', views.dashboard, name="dashboard"),

    path('test', views.open_test, name="test"),
    path('question/<int:qnumber>', views.get_question, name="get_question"),
    path('upload-answer', views.upload_answer, name="upload_answer"),
    path('answers/<int:qnumber>', views.get_answers, name="get_answers"),

    path('question-portal/<int:page>', views.question_making_page, name="questionportal"),
    path('post-question', views.post_question, name="post_question"),
    path('edit-question', views.edit_question, name="edit_question"),
    path('del-question', views.delete_question, name="del_question"),

    # path('drive-clear', views.drive_clear, name="drive_clear"),
    # path('drive-list', views.drive_list, name="drive_list"),
]
