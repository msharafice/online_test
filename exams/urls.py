from django.urls import path
from .views import exam, exam_form


urlpatterns = [
  path('', exam, name='exam_list'),
  path('form/', exam_form, name='add_exam'), 
  path('form/<int:pk>/', exam_form, name='edit_exam'), 
]