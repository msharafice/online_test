from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import Exam, Question, Choice


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ("title", "subject", "duration", "total_score", "start_time", "end_time")
        widgets = {
            "start_time": forms.DateInput(attrs={"type": "date"}),
            "end_time": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time > end_time:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("text", "question_type", "score")


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ("text",)


class ChoiceEditForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ("text", "is_correct")


class _ChoiceInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        correct_count = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            text = (form.cleaned_data.get("text") or "").strip()
            if not text:
                continue

            if form.cleaned_data.get("is_correct"):
                correct_count += 1

        if correct_count == 0:
            raise forms.ValidationError("باید حداقل یک گزینه صحیح باشد.")
        if correct_count > 1:
            raise forms.ValidationError("فقط یک گزینه می‌تواند صحیح باشد.")


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    formset=_ChoiceInlineFormSet,
    fields=("text", "is_correct"),
    extra=4,
    can_delete=True,
)
