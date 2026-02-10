from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def student_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_student():
            # اگر namespace users داری:
            return redirect("users:login")
            # اگر namespace نداری، اینو بذار:
            # return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
