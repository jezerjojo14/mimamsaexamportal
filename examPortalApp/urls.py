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
    path('instructions', views.instructions, name="instructions"),

    path('test/<int:qnumber>', views.open_test, name="test_no"),
    path('upload-answer', views.upload_answer, name="upload_answer"),
    path('upload-text-answer', views.upload_text_answer, name="upload_text_answer"),
    path('save-mcq', views.submit_MCQ, name="save_m_answer"),
    path('save-tt', views.submit_TT, name="save_t_answer"),
    path('answers/<int:qnumber>/<int:page_no>', views.get_answer, name="get_answer"),
    path('answers/delete/<int:qnumber>/<int:page_no>', views.del_answer, name="del_answer"),
    path('move-down', views.move_down, name="move_down"),
    path('move-up', views.move_up, name="move_up"),
    path('m-answers/<int:qnumber>', views.get_m_answers, name="get_m_answers"),
    path('t-answers/<int:qnumber>', views.get_t_answers, name="get_t_answers"),
    path('clear-t-options/<int:qnumber>', views.clear_t_options, name="clear_t_options"),
    path('del-question', views.delete_question, name="del_question"),
    path('review/<int:qnumber>', views.mark_for_review, name="review"),
    path('answered/<int:qnumber>', views.mark_as_answered, name="answered"),
    path('unanswered/<int:qnumber>', views.mark_as_unanswered, name="unanswered"),


    path('question-portal/<int:page>', views.question_making_page, name="questionportal"),
    path('post-question', views.post_question, name="post_question"),
    path('edit-question', views.edit_question, name="edit_question"),
    path('del-question', views.delete_question, name="del_question"),

    path('loaderio-bc4611489ba175954b1027ee937bd232/', views.loader),
    path('password-list', views.password_list, name="password_list"),
    path('email', views.mail_change, name="mail_change"),
    path('testmonkey', views.db_test),

    path('correction', views.correction_subject, name="correction_subject"),
    path('correction/<str:subject>', views.correction_question, name="correction_question"),
    path('correction/q/<int:question>/p/<int:page>', views.correction_team, name="correction_team"),
    path('correction/q/<int:question>/<str:sequence>', views.correction, name="correction"),
    path('toggle-graded-confirm', views.toggle_graded_confirm, name='toggle_graded_confirm'),
    # path('auto-correction', views.automated_correction, name="automated_correction"),

]
