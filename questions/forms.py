from django.forms import BaseInlineFormSet
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Question, Choice
from django import forms
from .models import Question, Choice
from django.forms import inlineformset_factory

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'score'] 

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']


class ChoiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        correct_count = 0

        for form in self.forms:
            # فرم‌های پاک‌شده یا خالی را نادیده بگیر
            if form.cleaned_data.get("DELETE"):
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
    formset=ChoiceFormSet,
    fields=("text", "is_correct"),
    extra=4,
    can_delete=True
)
