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