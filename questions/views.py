from django.shortcuts import render, redirect, get_object_or_404
<<<<<<< HEAD
from .models import Question, Choice
from .forms import QuestionForm, ChoiceFormSet
from exams.models import Exam

# -------------------- نمایش سوالات یک آزمون --------------------
def exam_questions(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.all()
    context = {
        'exam': exam,
        'questions': questions,
    }
    return render(request, 'exam_questions.html', context)

# -------------------- اضافه کردن سوال --------------------
def add_question(request, exam_id):
    # گرفتن آزمون از URL
    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam  
            question.save()
            return redirect('exam_questions', exam_id=exam.id)
    else:
        form = QuestionForm()

    context = {
        'form': form,
        'exam': exam,
        'is_edit': False,
    }
    return render(request, 'question_form.html', context)


# -------------------- ویرایش سوال --------------------
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('exam_questions', exam_id=question.exam.id)
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)

    context = {
        'form': form,
        'formset': formset,
        'exam': question.exam,
        'is_edit': True,
    }
    return render(request, 'question_form.html', context)

# -------------------- حذف سوال --------------------
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    exam_id = question.exam.id
    if request.method == 'POST':
        question.delete()
        return redirect('exam_questions', exam_id=exam_id)
    return render(request, 'question_confirm_delete.html', {'question': question})
#-------------------------------
def question_form(request, exam_id, pk=None):
    exam = get_object_or_404(Exam, pk=exam_id)

    if pk:
        question = get_object_or_404(Question, pk=pk, exam=exam)
    else:
        question = None

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)

        # فقط اگر چندگزینه‌ای است، ChoiceFormSet را بساز
        formset = None
        if form.is_valid() and form.cleaned_data["question_type"] == "mcq":
            formset = ChoiceFormSet(request.POST, instance=question)

        if form.is_valid() and (formset is None or formset.is_valid()):
            saved_question = form.save()

            # گزینه‌ها را ذخیره کنیم (فقط برای mcq)
            if form.cleaned_data["question_type"] == "mcq":
                formset.instance = saved_question
                formset.save()

            return redirect("question_list", exam_id=exam.id)

    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question) if (question and question.question_type == "mcq") else None

    return render(request, "question_form.html", {
        "form": form,
        "formset": formset,
        "exam": exam,
        "question": question,
    })
=======
from django import forms
import logging

from .models import Exam, Question, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm
from .decorators import teacher_required
from exams.models import ExamAttempt

logger = logging.getLogger("questions")


@teacher_required
def teacher_dashboard(request):
    exams = Exam.objects.filter(teacher=request.user)

    attempts = (
        ExamAttempt.objects
        .filter(exam__teacher=request.user)
        .select_related("exam", "student")
    )

    return render(request, "questions/dashboard.html", {
        "exams": exams,
        "attempts": attempts
    })


@teacher_required
def create_exam(request):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        exam = form.save(commit=False)
        exam.teacher = request.user
        exam.save()
        return redirect("questions:dashboard")
    return render(request, "questions/create_exam.html", {"form": form})


@teacher_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    exam.delete()
    return redirect("questions:dashboard")


@teacher_required
def exam_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    return render(request, "questions/exam_questions.html", {"exam": exam})


@teacher_required
def create_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

    form = QuestionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        question = form.save(commit=False)
        question.exam = exam
        question.save()
        return redirect("questions:add_choices", question_id=question.id)

    # ✅ مهم: exam رو پاس می‌دیم تا توی template exam.id داشته باشی
    return render(request, "questions/create_question.html", {
        "form": form,
        "exam": exam,
    })


@teacher_required
def add_choices(request, question_id):
    question = get_object_or_404(Question, id=question_id, exam__teacher=request.user)

    if question.question_type == "descriptive":
        return redirect("questions:exam_questions", exam_id=question.exam.id)

    forms_list = [ChoiceForm(request.POST or None, prefix=str(i)) for i in range(4)]

    if request.method == "POST":
        if all(f.is_valid() for f in forms_list):
            for f in forms_list:
                choice = f.save(commit=False)
                choice.question = question
                choice.save()
            return redirect("questions:exam_questions", exam_id=question.exam.id)

    return render(request, "questions/add_choices.html", {
        "forms": forms_list,
        "question": question
    })


@teacher_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, exam__teacher=request.user)

    question_form = QuestionForm(request.POST or None, instance=question)

    ChoiceFormSet = forms.modelformset_factory(Choice, form=ChoiceForm, extra=0, can_delete=True)
    formset = ChoiceFormSet(request.POST or None, queryset=question.choices.all())

    if request.method == "POST":
        if question_form.is_valid() and (question.question_type == "descriptive" or formset.is_valid()):
            question_form.save()

            if question.question_type == "test":
                instances = formset.save(commit=False)
                for obj in instances:
                    obj.question = question
                    obj.save()
                for obj in formset.deleted_objects:
                    obj.delete()

            return redirect("questions:exam_questions", exam_id=question.exam.id)

    return render(request, "questions/edit_question.html", {
        "question_form": question_form,
        "formset": formset,
        "question": question
    })


@teacher_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, exam__teacher=request.user)
    exam_id = question.exam.id
    question.delete()
    return redirect("questions:exam_questions", exam_id=exam_id)


@teacher_required
def publish_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    exam.is_published = True
    exam.save()
    return redirect("questions:exam_questions", exam_id=exam.id)
>>>>>>> faaf019 (last edit)
