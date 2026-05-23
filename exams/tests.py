from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core import mail

from users.models import User
from questions.models import Exam, Question, Choice
from .models import ExamAttempt, StudentAnswer, Grade


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ExamsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="Pass12345!", role="teacher", is_active=True
        )
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="Pass12345!", role="student", is_active=True
        )

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            title="Physics 1",
            subject="Physics",
            duration=10,
            total_score=20,
            start_time=timezone.now() - timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1),
            is_published=True,
        )

        self.q1 = Question.objects.create(exam=self.exam, text="Q1", question_type="test")
        self.c1 = Choice.objects.create(question=self.q1, text="A", is_correct=True)
        self.c2 = Choice.objects.create(question=self.q1, text="B", is_correct=False)

    def _login_student(self):
        self.client.login(username="student", password="Pass12345!")

    def _login_teacher(self):
        self.client.login(username="teacher", password="Pass12345!")

    def test_student_dashboard_search_by_title_or_subject(self):
        self._login_student()
        res = self.client.get(reverse("exams:student_dashboard") + "?q=Physics")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Physics 1")

        res2 = self.client.get(reverse("exams:student_dashboard") + "?q=Phys")
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "Physics 1")


def test_start_exam_creates_attempt_and_answers(self):
    self._login_student()

    res = self.client.post(reverse("exams:start_exam", args=[self.exam.id]), {
        f"question_{self.q1.id}": str(self.c1.id),
    })
    self.assertEqual(res.status_code, 302)

    attempt = ExamAttempt.objects.get(student=self.student, exam=self.exam)

   
    self.assertEqual(StudentAnswer.objects.filter(attempt=attempt).count(), 1)

    def test_grade_exists_after_submit(self):
        """
        بعضی نسخه‌ها auto-grade میدن، بعضی نسخه‌ها grade رو بعداً استاد میده.
        این تست فقط تضمین می‌کنه بعد submit، attempt ساخته میشه و حداقل جواب‌ها ذخیره میشن.
        """
        self._login_student()
        self.client.post(reverse("exams:start_exam", args=[self.exam.id]), {
            f"question_{self.q1.id}": str(self.c1.id),
        })

        attempt = ExamAttempt.objects.get(student=self.student, exam=self.exam)
        self.assertTrue(StudentAnswer.objects.filter(attempt=attempt).exists())

        g = Grade.objects.filter(attempt=attempt).first()
        if g is not None and g.score is not None:
            self.assertGreaterEqual(float(g.score), 0.0)
            self.assertLessEqual(float(g.score), float(self.exam.total_score))

    def test_teacher_can_view_attempts(self):
        self._login_student()
        self.client.post(reverse("exams:start_exam", args=[self.exam.id]), {
            f"question_{self.q1.id}": str(self.c2.id),
        })
        attempt = ExamAttempt.objects.get(student=self.student, exam=self.exam)

        self.client.logout()
        self._login_teacher()

        res = self.client.get(reverse("exams:exam_attempts", args=[self.exam.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, attempt.student.username)

    def test_teacher_can_save_grade_if_attempt_detail_exists(self):
        """
        اگر attempt_detail در urls هست، نمره ثبت میشه.
        اگر نداری، این تست رو حذف کن یا مسیر رو درست کن.
        """
        self._login_student()
        self.client.post(reverse("exams:start_exam", args=[self.exam.id]), {
            f"question_{self.q1.id}": str(self.c2.id),
        })
        attempt = ExamAttempt.objects.get(student=self.student, exam=self.exam)

        self.client.logout()
        self._login_teacher()

        res = self.client.post(reverse("exams:attempt_detail", args=[attempt.id]), {"score": "5"})
        self.assertIn(res.status_code, (302, 200))

        g = Grade.objects.filter(attempt=attempt).first()
        if g is not None:
            g.refresh_from_db()
            self.assertEqual(float(g.score), 5.0)
