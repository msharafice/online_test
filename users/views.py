from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .forms import SignUpForm
from .models import User

import logging
logger = logging.getLogger("users")


def signup_view(request):
    error = None

    # ------------- مرحله تایید کد -------------
    verify_user_id = request.session.get("verify_user_id")
    if verify_user_id:
        try:
            user = User.objects.get(id=verify_user_id)
        except User.DoesNotExist:
            logger.warning("Email verification session had invalid user id")
            request.session.pop("verify_user_id", None)
            return redirect("users:signup")

        if request.method == "POST" and request.POST.get("code") is not None:
            code = (request.POST.get("code") or "").strip()

            if user.email_code and code == user.email_code:
                user.is_active = True
                user.is_email_verified = True
                user.email_code = None
                user.save()

                request.session.pop("verify_user_id", None)

                login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                logger.info(
                    f"Email verified user_id={user.id} email={user.email} username={user.username}"
                )
                return redirect("users:redirect")
            else:
                logger.warning(
                    f"Wrong verification code user_id={user.id} email={user.email}"
                )
                error = "کد وارد شده اشتباه است"

        return render(
            request,
            "users/signup.html",
            {
                "form": None,
                "show_code_form": True,
                "error": error,
            },
        )

    # ------------- مرحله ثبت‌نام -------------
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.generate_email_code()
            user.save()

            logger.info(
                f"Signup created user_id={user.id} email={user.email} role={user.role}"
            )

            try:
                send_mail(
                    subject="Email Verification Code",
                    message=f"Your verification code is: {user.email_code}",
                    from_email=getattr(
                        settings,
                        "DEFAULT_FROM_EMAIL",
                        settings.EMAIL_HOST_USER,
                    ),
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                logger.info(
                    f"Verification email sent user_id={user.id} email={user.email}"
                )

            except Exception as e:
                logger.error(
                    f"Email send failed user_id={user.id} email={user.email} err={e}",
                    exc_info=True,
                )
                error = "ارسال ایمیل با مشکل مواجه شد. تنظیمات ایمیل را چک کنید."
                return render(
                    request,
                    "users/signup.html",
                    {
                        "form": form,
                        "show_code_form": False,
                        "error": error,
                    },
                )

            request.session["verify_user_id"] = user.id
            return redirect("users:signup")

        else:
            logger.warning("Signup form invalid")
            error = "فرم نامعتبر است. موارد را بررسی کنید."

    else:
        form = SignUpForm()

    return render(
        request,
        "users/signup.html",
        {
            "form": form,
            "show_code_form": False,
            "error": error,
        },
    )


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        logger.info(
            f"Login success user_id={user.id} username={user.username} role={getattr(user, 'role', None)}"
        )
        return response

    def form_invalid(self, form):
        username = self.request.POST.get("username", "")
        logger.warning(f"Login failed username={username}")
        return super().form_invalid(form)


def custom_logout(request):
    user_id = request.user.id if request.user.is_authenticated else None
    username = request.user.username if request.user.is_authenticated else None

    logout(request)

    logger.info(f"Logout user_id={user_id} username={username}")
    return redirect("users:login")


@login_required
def redirect_view(request):
    # این روت فقط جهت هدایت بعد از لاگین هست
    if request.user.is_teacher():
        logger.info(f"Redirect teacher user_id={request.user.id}")
        return redirect("questions:dashboard")

    logger.info(f"Redirect student user_id={request.user.id}")
    return redirect("exams:student_dashboard")
