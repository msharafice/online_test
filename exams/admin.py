from django.contrib import admin
from .models import ExamAttempt, StudentAnswer, Grade

admin.site.register(ExamAttempt)
admin.site.register(StudentAnswer)
admin.site.register(Grade)
