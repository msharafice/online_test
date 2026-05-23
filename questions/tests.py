from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from users.models import User
from .models import Exam, Question, Choice


class QuestionsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="Pass12345!", role="teacher", is_active=True
        )
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="Pass12345!", role="student", is_active=True
        )

    def _login_teacher(self):
        self.client.login(username="teacher", password="Pass12345!")

    def _login_student(self):
        self.client.login(username="student", password="Pass12345!")

    def test_teacher_required_dashboard(self):
        self._login_student()
        res = self.client.get(reverse("questions:dashboard"))
        self.assertEqual(res.status_code, 302)  # باید برگرده لاگین

    def test_create_exam_teacher(self):
        self._login_teacher()
        res = self.client.post(reverse("questions:create_exam"), {
            "title": "Math Exam",
            "subject": "Math",
            "duration": 10,
            "total_score": 20,
            "start_time": (timezone.now()).date(),
            "end_time": (timezone.now() + timedelta(days=1)).date(),
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Exam.objects.filter(title="Math Exam", teacher=self.teacher).exists())

    def test_add_question_and_choices(self):
        self._login_teacher()
        exam = Exam.objects.create(
            teacher=self.teacher,
            title="E1",
            subject="S1",
            duration=10,
            total_score=20,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            is_published=False,
        )

        res = self.client.post(reverse("questions:create_question", args=[exam.id]), {
            "text": "Q1?",
            "question_type": "test",
        })
        self.assertEqual(res.status_code, 302)
        q = Question.objects.get(exam=exam, text="Q1?")

        res = self.client.post(reverse("questions:add_choices", args=[q.id]), {
            "0-text": "A",
            "0-is_correct": "on",
            "1-text": "B",
            "2-text": "C",
            "3-text": "D",
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Choice.objects.filter(question=q).count(), 4)

    def test_publish_exam(self):
        self._login_teacher()
        exam = Exam.objects.create(
            teacher=self.teacher,
            title="E2",
            subject="S2",
            duration=10,
            total_score=20,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            is_published=False,
        )
        res = self.client.get(reverse("questions:publish_exam", args=[exam.id]))
        self.assertEqual(res.status_code, 302)
        exam.refresh_from_db()
        self.assertTrue(exam.is_published)
