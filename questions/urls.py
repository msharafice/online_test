from django.urls import path
from . import views

<<<<<<< HEAD
urlpatterns = [
    path('exam/<int:exam_id>/', views.exam_questions, name='exam_questions'),
    path('exam/<int:exam_id>/add/', views.add_question, name='add_question'),
    path('question/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
]
=======
app_name = 'questions'

urlpatterns = [
    path('', views.teacher_dashboard, name='dashboard'),
    path('create-exam/', views.create_exam, name='create_exam'),
    path('delete-exam/<int:exam_id>/', views.delete_exam, name='delete_exam'),
    path('exam/<int:exam_id>/', views.exam_questions, name='exam_questions'),
    path('exam/<int:exam_id>/add-question/', views.create_question, name='create_question'),
    path('add-choices/<int:question_id>/', views.add_choices, name='add_choices'),
    path('exam/<int:exam_id>/publish/', views.publish_exam, name='publish_exam'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),


]
>>>>>>> faaf019 (last edit)
