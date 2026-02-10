from django.contrib import admin
from .models import Exam, Question, Choice
# Register your models here.

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Choice)