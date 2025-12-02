from django.shortcuts import render, redirect, get_object_or_404
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
