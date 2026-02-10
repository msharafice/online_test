from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher():
            return redirect("users:login")  # ✅ اصلاح شد
        return view_func(request, *args, **kwargs)
    return wrapper
