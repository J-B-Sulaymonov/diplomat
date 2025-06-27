# apply/resources.py

from import_export import resources
from import_export.widgets import ForeignKeyWidget
from .models import Question, Sciences

class QuestionResource(resources.ModelResource):
    sciences = resources.Field(
        column_name='sciences',
        attribute='sciences',
        widget=ForeignKeyWidget(Sciences, 'name'))

    class Meta:
        model = Question
        fields = ('id', 'question', 'A', 'B', 'C', 'D', 'correct_answer', 'language', 'sciences', 'status', 'author')
        skip_unchanged = True
        report_skipped = True