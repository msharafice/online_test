from django.db import models
from django.conf import settings
from questions.models import Exam, Question, Choice

User = settings.AUTH_USER_MODEL


class ExamAttemptManager(models.Manager):
    def by_student(self, student):
        return self.filter(student=student)

    def by_exam(self, exam):
        return self.filter(exam=exam)

    def finished(self):
        return self.filter(is_finished=True)

    def ungraded(self):
        return self.filter(grade__isnull=True)


class GradeManager(models.Manager):
    def by_student(self, student):
        return self.filter(attempt__student=student)

    def by_exam(self, exam):
        return self.filter(attempt__exam=exam)


class ExamAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')

    started_at = models.DateTimeField(auto_now_add=True)

    finished_at = models.DateTimeField(null=True, blank=True)

    is_finished = models.BooleanField(default=False)

    objects = ExamAttemptManager()

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f'{self.student} - {self.exam}'


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_choice = models.ForeignKey(
        Choice, null=True, blank=True, on_delete=models.SET_NULL
    )

    descriptive_answer = models.TextField(blank=True)

    uploaded_file = models.FileField(
        upload_to='answers/',
        blank=True,
        null=True
    )

    def correct_choice(self):
        return self.question.choices.filter(is_correct=True).first()

    def is_correct(self):
        if self.selected_choice:
            return self.selected_choice.is_correct
        return None

    def __str__(self):
        return f'{self.attempt} - {self.question}'


class Grade(models.Model):
    attempt = models.OneToOneField(ExamAttempt, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    objects = GradeManager()

    def __str__(self):
        return f'{self.attempt} - {self.score}'
