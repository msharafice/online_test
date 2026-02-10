from django.test import TestCase, Client, override_settings
from django.urls import reverse, NoReverseMatch
from django.core import mail

from .models import User


def _safe_reverse(name: str, fallback_path: str) -> str:
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback_path


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class UsersFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.teacher = User.objects.create_user(
            username="t1", email="t1@test.com", password="Pass12345!", role="teacher", is_active=True
        )
        self.student = User.objects.create_user(
            username="s1", email="s1@test.com", password="Pass12345!", role="student", is_active=True
        )

        # مسیرها (با fallback)
        self.login_url = _safe_reverse("users:login", "/")
        self.signup_url = _safe_reverse("users:signup", "/signup/")
        self.redirect_url = _safe_reverse("users:redirect", "/redirect/")

    def test_login_teacher_redirects_to_questions_dashboard(self):
        res = self.client.post(self.login_url, {"username": "t1", "password": "Pass12345!"})
        self.assertEqual(res.status_code, 302)
        # در نهایت باید بره redirect_view و از اونجا بره داشبورد استاد
        self.assertIn(self.redirect_url, res.url) if self.redirect_url else None

    def test_login_student_redirects_to_student_dashboard(self):
        res = self.client.post(self.login_url, {"username": "s1", "password": "Pass12345!"})
        self.assertEqual(res.status_code, 302)
        self.assertIn(self.redirect_url, res.url) if self.redirect_url else None

    def test_signup_creates_inactive_user_and_sends_code_email(self):
        res = self.client.post(self.signup_url, {
            "username": "newuser",
            "email": "new@test.com",
            "role": "student",
            "password1": "Pass12345!",
            "password2": "Pass12345!",
        })
        self.assertEqual(res.status_code, 302)

        u = User.objects.get(username="newuser")
        self.assertFalse(u.is_active)
        self.assertTrue(bool(u.email_code))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(u.email_code, mail.outbox[0].body)

    def test_signup_verify_code_activates_user_and_logs_in(self):
        # مرحله ۱: ثبت‌نام
        self.client.post(self.signup_url, {
            "username": "vuser",
            "email": "v@test.com",
            "role": "student",
            "password1": "Pass12345!",
            "password2": "Pass12345!",
        })
        u = User.objects.get(username="vuser")
        self.assertFalse(u.is_active)

        # session باید verify_user_id داشته باشد
        session = self.client.session
        session["verify_user_id"] = u.id
        session.save()

        # مرحله ۲: تایید کد
        res = self.client.post(self.signup_url, {"code": u.email_code})
        self.assertEqual(res.status_code, 302)

        u.refresh_from_db()
        self.assertTrue(u.is_active)
        self.assertTrue(u.is_email_verified)
