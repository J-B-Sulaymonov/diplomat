from django import forms
from .models import Question

class QuestionImportForm(forms.ModelForm):
    upload_file = forms.FileField(required=False, label="Fayldan yuklash")

    class Meta:
        model = Question
        fields = '__all__'
