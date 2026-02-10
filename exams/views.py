<<<<<<< HEAD
from django.shortcuts import get_object_or_404, render, redirect
from .models import Exam
from .forms import ExamForm
from django.utils import timezone 

# Create your views here.


def exam(request):
  exams = Exam.objects.all()
  
  if request.method == "POST":
    exam_id = request.POST.get('delete_id')
    if exam_id:
        exam_to_delete = get_object_or_404(Exam, pk=exam_id)
        exam_to_delete.delete()
        return redirect('exam_list')

  context = {
    'exams':exams
  }
  return render(request,'exam.html', context)


def exam_form(request, pk=None):
    if pk:
        exam = get_object_or_404(Exam, pk=pk)
    else:
        exam = None

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            exam_obj = form.save(commit=False)
            if not pk:  # فقط برای رکورد جدید
                exam_obj.instructor = request.user
                exam_obj.start_time = timezone.now()
            exam_obj.save()
            return redirect('exam_list') 
    else:
        form = ExamForm(instance=exam)

    context = {
        'form': form,
        'is_edit': bool(pk),
    }
    return render(request, 'form.html', context)
=======
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import logging
from django.shortcuts import redirect

from questions.models import Exam
from .models import ExamAttempt, StudentAnswer, Grade
from .decorators import student_required
from questions.decorators import teacher_required

logger = logging.getLogger("exams")


# ================== AUTO SCORE ==================
def _compute_auto_score(exam: Exam, answers: list[StudentAnswer]) -> float:
    test_questions = list(
        exam.questions.filter(question_type="test").prefetch_related("choices")
    )
    total_tests = len(test_questions)
    if total_tests == 0:
        return 0.0

    correct_map = {}
    for q in test_questions:
        c = q.choices.filter(is_correct=True).first()
        correct_map[q.id] = c.id if c else None

    correct = 0
    for a in answers:
        if a.question_id in correct_map and correct_map[a.question_id] == a.selected_choice_id:
            correct += 1

    total_score = float(exam.total_score or 0)
    return round((correct / total_tests) * total_score, 2)


def _has_descriptive(exam: Exam) -> bool:
    return exam.questions.filter(question_type="descriptive").exists()


def _send_grade_email(student_email, exam_title, score, total):
    send_mail(
        subject=f"Grade Result - {exam_title}",
        message=f"Score: {score} / {total}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
        recipient_list=[student_email],
        fail_silently=True,
    )


# ================== STUDENT ==================
@student_required
def student_dashboard(request):
    q = request.GET.get("q", "").strip()

    exams = Exam.objects.filter(is_published=True)
    if q:
        exams = exams.filter(Q(title__icontains=q) | Q(subject__icontains=q)).distinct()

    today = timezone.localdate()
    exam_info = []

    for exam in exams:
        attempt = ExamAttempt.objects.filter(student=request.user, exam=exam).first()
        grade = Grade.objects.filter(attempt=attempt).first() if attempt else None

        if exam.start_time.date() > today:
            status, can_start = "Not Started Yet", False
        elif exam.end_time.date() < today:
            status, can_start = "Finished", False
        else:
            if attempt:
                status = f"Score: {grade.score}" if grade else "Waiting for grade"
                can_start = False
            else:
                status, can_start = "Start", True

        exam_info.append({"exam": exam, "status": status, "can_start": can_start})

    return render(request, "exams/student_dashboard.html", {
        "exam_info": exam_info,
        "query": q,
    })


@student_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    if ExamAttempt.objects.filter(student=request.user, exam=exam).exists():
        return redirect("exams:student_dashboard")

    if request.method == "POST":
        attempt = ExamAttempt.objects.create(student=request.user, exam=exam)
        answers = []

        for q in exam.questions.all():
            if q.question_type == "test":
                ans = StudentAnswer.objects.create(
                    attempt=attempt,
                    question=q,
                    selected_choice_id=request.POST.get(f"question_{q.id}")
                )
            else:
                ans = StudentAnswer.objects.create(
                    attempt=attempt,
                    question=q,
                    descriptive_answer=request.POST.get(f"text_question_{q.id}", "").strip(),
                    uploaded_file=request.FILES.get(f"file_question_{q.id}")
                )
            answers.append(ans)

        # auto score
        auto_score = _compute_auto_score(exam, answers)

        grade, _ = Grade.objects.get_or_create(attempt=attempt)
        grade.score = auto_score
        grade.save()

        # اگر تشریحی ندارد → تمام
        if not _has_descriptive(exam):
            _send_grade_email(
                request.user.email,
                exam.title,
                grade.score,
                exam.total_score,
            )

        return redirect("exams:student_dashboard")

    return render(request, "exams/start_exam.html", {"exam": exam})


# ================== TEACHER ==================
@teacher_required
def exam_attempts(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    attempts = ExamAttempt.objects.filter(exam=exam)
    return render(request, "exams/exam_attempts.html", {
        "exam": exam,
        "attempts": attempts,
    })


@teacher_required
def attempt_detail(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related("exam", "student"),
        id=attempt_id,
        exam__teacher=request.user,
    )

    grade, _ = Grade.objects.get_or_create(attempt=attempt)
    exam_total = float(attempt.exam.total_score)
    test_score = float(grade.score or 0)
    remaining = max(exam_total - test_score, 0)

    if request.method == "POST":
        try:
            desc_score = float(request.POST.get("score"))
        except (TypeError, ValueError):
            return redirect("exams:attempt_detail", attempt_id=attempt.id)

        if 0 <= desc_score <= remaining:
            grade.score = test_score + desc_score
            grade.save()

            _send_grade_email(
                attempt.student.email,
                attempt.exam.title,
                grade.score,
                exam_total,
            )

            return redirect("exams:exam_attempts", exam_id=attempt.exam.id)

        return redirect("exams:attempt_detail", attempt_id=attempt.id)

    return render(request, "exams/attempt_detail.html", {
        "attempt": attempt,
        "answers": attempt.answers.all(),
        "grade": grade,
        "test_score": test_score,
        "remaining_score": remaining,
        "exam_total": exam_total,
    })
@teacher_required
def grade_exam(request, attempt_id):
    return redirect("exams:attempt_detail", attempt_id=attempt_id)
>>>>>>> faaf019 (last edit)
