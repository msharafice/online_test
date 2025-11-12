from django.db import models
from exams.models import Exam
from django.contrib.auth.models import User


class Question(models.Model):
    QUESTION_TYPES = [
        ('short', 'پاسخ کوتاه'),
        ('mcq', 'چندگزینه‌ای'),
        ('file', 'فایل‌دار'),
    ]
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    score = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.text[:50]}..."


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    file_upload = models.FileField(upload_to='answers/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
