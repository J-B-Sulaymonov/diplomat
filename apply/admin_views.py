import json
import zipfile

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Question, Sciences
import re
import ast

def question_save(quiz, science_id, language, author_id=1):
    for i in quiz:
        if len(quiz[i]['options']) == 4:
            answer = quiz[i]['correct'].lower()
            if answer in ['a', 'b', 'c', 'd']:
                question_text = quiz[i]['mcq'].replace("\\(", '$').replace("\\)", '$').replace("\_", '_').replace("\\textless{}","<").replace("\\textgreater{}",">").replace("\\textless","<").replace("\\textgreater",">").replace('{[}',"[").replace('{]}',"]").replace('--',"-")
                question_text=re.sub(r'\\ldots(\{\})?', r'...', question_text)

                options = quiz[i]['options']
                correct_upper = answer.upper()

                Question.objects.create(
                    sciences_id=science_id,
                    language=language,
                    author_id=author_id,
                    status=True,
                    question=question_text,
                    A=options['a'].replace("\\(", '$').replace("\\)", '$').replace("\_", '_').replace("\\textless{}","<").replace("\\textgreater{}",">").replace("\\textless","<").replace("\\textgreater",">").replace("\ldots{}","$\ldots$").replace("\ldots","$\ldots$").replace('{[}',"[").replace('{]}',"]").replace('--',"-"),
                    B=options['b'].replace("\\(", '$').replace("\\)", '$').replace("\_", '_').replace("\\textless{}","<").replace("\\textgreater{}",">").replace("\\textless","<").replace("\\textgreater",">").replace("\ldots{}","$\ldots$").replace("\ldots","$\ldots$").replace('{[}',"[").replace('{]}',"]").replace('--',"-"),
                    C=options['c'].replace("\\(", '$').replace("\\)", '$').replace("\_", '_').replace("\\textless{}","<").replace("\\textgreater{}",">").replace("\\textless","<").replace("\\textgreater",">").replace("\ldots{}","$\ldots$").replace("\ldots","$\ldots$").replace('{[}',"[").replace('{]}',"]").replace('--',"-"),
                    D=options['d'].replace("\\(", '$').replace("\\)", '$').replace("\_", '_').replace("\\textless{}","<").replace("\\textgreater{}",">").replace("\\textless","<").replace("\\textgreater",">").replace("\ldots{}","$\ldots$").replace("\ldots","$\ldots$").replace('{[}',"[").replace('{]}',"]").replace('--',"-"),
                    correct_answer=correct_upper
                )
    return True
@staff_member_required
def upload_question_file(request):

    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        science_id = request.POST.get("science")
        language = request.POST.get("language")
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                files = zip_ref.infolist()
                for my_file in files:
                    if str(my_file.filename) == "import.txt":
                        file = my_file
                        with zip_ref.open(file, "r") as questions:
                            json_content = str(json.load(questions))
                            text = json.dumps(
                                json_content.replace('\x92', "'").replace("\\\(", '$').replace("\\\)", '$'))
                            quiz = ast.literal_eval(json.loads(text))
                            test=question_save(quiz, science_id, language, 1)

        return redirect('/admin/apply/question/')
    sciences = Sciences.objects.all()
    return render(request, 'admin/apply/question/upload_question.html',{'sciences':sciences})
