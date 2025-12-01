from django.urls import path
from . import views

urlpatterns = [
    path('exam/<int:exam_id>/', views.exam_questions, name='exam_questions'),
    path('exam/<int:exam_id>/add/', views.add_question, name='add_question'),
    path('question/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
]