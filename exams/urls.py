from django.urls import path
<<<<<<< HEAD
from .views import exam, exam_form


urlpatterns = [
  path('', exam, name='exam_list'),
  path('form/', exam_form, name='add_exam'), 
  path('form/<int:pk>/', exam_form, name='edit_exam'), 
]
=======
from . import views

app_name = "exams"

urlpatterns = [
    # داشبورد دانشجو (لیست آزمون‌ها)
    path("", views.student_dashboard, name="student_dashboard"),

    # شروع آزمون
    path("start/<int:exam_id>/", views.start_exam, name="start_exam"),

    # لیست تلاش‌های یک آزمون برای استاد
    path("exam/<int:exam_id>/attempts/", views.exam_attempts, name="exam_attempts"),

    # جزئیات یک تلاش + ثبت نمره (قالب attempt_detail.html)
    path("attempt/<int:attempt_id>/", views.attempt_detail, name="attempt_detail"),

    # صفحه جدا برای نمره‌دهی (اگر هنوز از grade_exam.html استفاده می‌کنی)
    path("grade/<int:attempt_id>/", views.grade_exam, name="grade_exam"),
]
>>>>>>> faaf019 (last edit)
