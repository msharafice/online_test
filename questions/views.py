import logging
from django import forms
from django.shortcuts import render, redirect, get_object_or_404

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

    logger.info(
        f"Teacher dashboard teacher_id={request.user.id} exams_count={exams.count()} attempts_count={attempts.count()}"
    )

    return render(request, "questions/dashboard.html", {
        "exams": exams,
        "attempts": attempts,
    })


@teacher_required
def create_exam(request):
    form = ExamForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        exam = form.save(commit=False)
        exam.teacher = request.user
        exam.save()

        logger.info(
            f"Exam created teacher_id={request.user.id} exam_id={exam.id} title={exam.title}"
        )

        return redirect("questions:dashboard")

    return render(request, "questions/create_exam.html", {"form": form})


@teacher_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

    logger.info(
        f"Exam deleted teacher_id={request.user.id} exam_id={exam.id} title={exam.title}"
    )

    if request.method == "POST":
        exam.delete()
        return redirect("questions:dashboard")

    return render(request, "exams/delete_exam.html", {"exam": exam})
    


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

        logger.info(
            f"Question created teacher_id={request.user.id} exam_id={exam.id} question_id={question.id} type={question.question_type}"
        )

        return redirect("questions:add_choices", question_id=question.id)

    return render(request, "questions/create_question.html", {
        "form": form,
        "exam": exam,
    })


@teacher_required
def add_choices(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        exam__teacher=request.user,
    )

    if question.question_type == "descriptive":
        return redirect("questions:exam_questions", exam_id=question.exam.id)

    forms_list = [ChoiceForm(request.POST or None, prefix=str(i)) for i in range(4)]

    if request.method == "POST":
        correct_index_raw = request.POST.get("correct_index", None)

        if correct_index_raw is None:
            return render(request, "questions/add_choices.html", {
                "forms": forms_list,
                "question": question,
                "error": "Please select which choice is correct.",
            })

        try:
            correct_index = int(correct_index_raw)
        except ValueError:
            return render(request, "questions/add_choices.html", {
                "forms": forms_list,
                "question": question,
                "error": "Invalid correct choice selection.",
            })

        if all(f.is_valid() for f in forms_list):
            question.choices.all().delete()

            for i, f in enumerate(forms_list):
                choice = f.save(commit=False)
                choice.question = question

                choice.is_correct = (i == correct_index)

                choice.save()

            logger.info(
                f"Choices added teacher_id={request.user.id} question_id={question.id} correct_index={correct_index}"
            )

            return redirect("questions:exam_questions", exam_id=question.exam.id)

    return render(request, "questions/add_choices.html", {
        "forms": forms_list,
        "question": question,
    })




@teacher_required
def edit_question(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        exam__teacher=request.user,
    )

    question_form = QuestionForm(request.POST or None, instance=question)

    ChoiceFormSet = forms.modelformset_factory(
        Choice,
        form=ChoiceForm,
        extra=0,
        can_delete=True,
    )
    formset = ChoiceFormSet(request.POST or None, queryset=question.choices.all())

    if request.method == "POST":
        if question_form.is_valid() and (
            question.question_type == "descriptive" or formset.is_valid()
        ):
            question_form.save()

            if question.question_type == "test":
                instances = formset.save(commit=False)
                for obj in instances:
                    obj.question = question
                    obj.save()
                for obj in formset.deleted_objects:
                    obj.delete()

            logger.info(
                f"Question edited teacher_id={request.user.id} question_id={question.id}"
            )

            return redirect("questions:exam_questions", exam_id=question.exam.id)

    return render(request, "questions/edit_question.html", {
        "question_form": question_form,
        "formset": formset,
        "question": question,
    })


@teacher_required
def delete_question(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        exam__teacher=request.user,
    )
    exam_id = question.exam.id

    logger.info(
        f"Question deleted teacher_id={request.user.id} question_id={question.id} exam_id={exam_id}"
    )

    question.delete()
    return redirect("questions:exam_questions", exam_id=exam_id)


@teacher_required
def publish_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    exam.is_published = True
    exam.save()

    logger.info(
        f"Exam published teacher_id={request.user.id} exam_id={exam.id} title={exam.title}"
    )

    return redirect("questions:exam_questions", exam_id=exam.id)
