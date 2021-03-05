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

    path('test/<int:qnumber>', views.open_test, name="test_no"),
    path('upload-answer', views.upload_answer, name="upload_answer"),
    path('save-mcq', views.submit_MCQ, name="save_m_answer"),
    path('save-tt', views.submit_TT, name="save_t_answer"),
    path('answers/<int:qnumber>', views.get_answers, name="get_answers"),
    path('m-answers/<int:qnumber>', views.get_m_answers, name="get_m_answers"),
    path('t-answers/<int:qnumber>', views.get_t_answers, name="get_t_answers"),

    path('question-portal/<int:page>', views.question_making_page, name="questionportal"),
    path('post-question', views.post_question, name="post_question"),
    path('edit-question', views.edit_question, name="edit_question"),
    path('del-question', views.delete_question, name="del_question"),
]
