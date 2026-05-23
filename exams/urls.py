from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    path("", views.student_dashboard, name="student_dashboard"),

    path("start/<int:exam_id>/", views.start_exam, name="start_exam"),

    path("exam/<int:exam_id>/attempts/", views.exam_attempts, name="exam_attempts"),
    path("attempt/<int:attempt_id>/", views.attempt_detail, name="attempt_detail"),

    path("grade/<int:attempt_id>/", views.grade_exam, name="grade_exam"),
    path("export-excel/<int:exam_id>/", views.export_attempts_to_excel, name="export_excel"),
]
