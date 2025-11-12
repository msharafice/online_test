from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Exam(models.Model):
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    total_score = models.IntegerField()
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='exams_created')

    def __str__(self):
        return self.title