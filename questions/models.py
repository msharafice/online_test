from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# =====================
# Managers
# =====================

class ExamManager(models.Manager):
    def published(self):
        return self.filter(is_published=True)

    def by_teacher(self, teacher):
        return self.filter(teacher=teacher)


class QuestionManager(models.Manager):
    def tests(self):
        return self.filter(question_type="test")

    def descriptives(self):
        return self.filter(question_type="descriptive")


# =====================
# Models
# =====================

class Exam(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    title = models.CharField(max_length=200)
    subject = models.CharField(
        max_length=100,
        default="General"   
    )

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    total_score = models.FloatField(
        default=0,
        help_text="Total exam score"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ExamManager()  

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ("test", "Test"),
        ("descriptive", "Descriptive"),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES
    )

    score = models.FloatField(
        default=1,
        help_text="Score for this question"
    )

    objects = QuestionManager()

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )

    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
