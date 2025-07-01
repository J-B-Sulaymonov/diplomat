import json
import uuid

from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from .models import Dagree, DirectionOfEducation, Region, ApplicationForm, Question
from django.core.exceptions import ObjectDoesNotExist
import logging
import random


logger = logging.getLogger(__name__)


def set_language(request, language):
    http_referer = request.META.get("HTTP_REFERER")
    if not http_referer:
        response = HttpResponseRedirect('/')
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response

    translation.activate(language)

    response = HttpResponseRedirect(http_referer)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

    return response


@require_http_methods(["GET", "POST"])
def application_form_view(request):

    if request.method == 'GET':
        try:
            degrees = Dagree.objects.filter(status=True)
            regions = Region.objects.all()
            context = {
                'degrees': degrees,
                'regions': regions,
            }
            return render(request, 'apply/index.html', context)
        except Exception as e:
            error_message = _("Error loading page: {}").format(e)
            logger.error(f"Error in GET request: {str(e)}")
            return render(request, 'apply/error.html', {'error': error_message})

    elif request.method == 'POST':
        data = request.POST
        files = request.FILES
        print(1)

        try:
            # Validation
            required_fields = ['degree', 'education_direction', 'study_form','language', 'surname',
                               'first_name', 'gender', 'phone', 'passport', 'jshir',
                               'address_of_permanent_residence', 'region']

            errors = {}
            for field in required_fields:
                if not data.get(field):
                    errors[field] = _("This field is required.")

            # File validations
            required_files = {
                'photo': _("Photo upload is required."),
                'passport_copy': _("Passport copy is required."),
                'diploma': _("Diploma is required.")
            }

            for file_field, error_msg in required_files.items():
                if file_field not in files:
                    errors[file_field] = error_msg

            # Conditional validation for DTM
            if data.get('has_dtm') == 'on':
                if not data.get('dtm_ball'):
                    errors['dtm_ball'] = _("DTM score is required when submitting DTM results.")
                if 'dtm_file' not in files:
                    errors['dtm_file'] = _("DTM document is required when submitting DTM results.")

            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            with transaction.atomic():
                # Get related objects
                dagree_obj = Dagree.objects.get(id=data['degree'])
                direction_obj = DirectionOfEducation.objects.get(id=data['education_direction'])
                region_obj = Region.objects.get(id=data['region'])

                # Create application
                app_data = {
                    'dagree': dagree_obj,
                    'direction_of_education': direction_obj,
                    'form_of_education': data['study_form'],
                    'language': data['language'],
                    'surname': data['surname'],
                    'first_name': data['first_name'],
                    'middle_name': data.get('middle_name', ''),
                    'gender': data['gender'],
                    'phone': data['phone'],
                    'telegram': data.get('telegram', ''),
                    'passport': data['passport'].upper(),
                    'jshir': data['jshir'],
                    'address_of_permanent_residence': data['address_of_permanent_residence'],
                    'region': region_obj,
                    'photo': files['photo'],
                    'passport_copy': files['passport_copy'],
                    'diploma': files['diploma'],
                    'additional_documents': files.get('additional_documents'),
                    'additional_documents_status': data.get('has_additional_docs') == 'on',
                    'dtm_ball': data.get('dtm_ball') if data.get('has_dtm') == 'on' else None,
                    'dtm_file': files.get('dtm_file') if data.get('has_dtm') == 'on' else None,
                    'dtm_status': data.get('has_dtm') == 'on',
                }

                new_application = ApplicationForm.objects.create(**app_data)
                short_uuid = str(uuid.uuid4()).split('-')[0]
                app_number = f"DU-{new_application.id:06d}-{short_uuid}"
                new_application.application_number = app_number
                new_application.save()

                return JsonResponse({
                    'success': True,
                    'application_number': app_number
                })

        except (Dagree.DoesNotExist, DirectionOfEducation.DoesNotExist, Region.DoesNotExist) as e:
            logger.error(f"Object not found: {str(e)}")
            return JsonResponse({
                'success': False,
                'errors': {'server_error': _('Selected data not found.')}
            }, status=400)

        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return JsonResponse({
                'success': False,
                'errors': {'server_error': _('Internal server error occurred.')}
            }, status=500)


@require_POST
def check_application_status(request):
    application_number = request.POST.get('application_number', '').strip()

    if not application_number:
        return JsonResponse({
            'success': False,
            'error': _('Application number is required')
        }, status=400)

    try:
        application = ApplicationForm.objects.get(application_number=application_number)
        return JsonResponse({
            'success': True,
            'status': application.status,
            'status_display': application.get_status_display(),
            'test_status': application.test_status,
            'application_number': application.application_number,
        })

    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Application not found with this number')
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': _('An error occurred: {}').format(str(e))
        }, status=500)
def get_directions(request, degree_id):
    try:
        directions = DirectionOfEducation.objects.filter(dagree_id=degree_id, status=True).values('id', 'name')
        return JsonResponse(list(directions), safe=False)
    except Exception:
        return JsonResponse([], safe=False)


def get_study_forms(request, direction_id):
    try:
        direction = DirectionOfEducation.objects.get(id=direction_id)
        forms = []
        if direction.personally:
            forms.append({'id': 'personally', 'name': _("Full-time education")})
        if direction.externally:
            forms.append({'id': 'externally', 'name': _("Externally education")})
        if direction.remote:
            forms.append({'id': 'remote', 'name': _("Distance learning")})
        return JsonResponse(forms, safe=False)
    except DirectionOfEducation.DoesNotExist:
        return JsonResponse([], safe=False)


def check_uniqueness(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            passport_value = data.get('passport')
            jshir_value = data.get('jshir')

            errors = {}

            if passport_value and ApplicationForm.objects.filter(passport=passport_value.upper()).exists():
                errors['passport'] = _('This passport number is already registered.')

            if jshir_value and ApplicationForm.objects.filter(jshir=jshir_value).exists():
                errors['jshir'] = _('This JSHIR (PINFL) is already registered.')

            if errors:
                return JsonResponse({'is_unique': False, 'errors': errors})
            else:
                return JsonResponse({'is_unique': True})

        except json.JSONDecodeError:
            return JsonResponse({'is_unique': False, 'errors': {'general': _('Invalid request.')}}, status=400)
    return JsonResponse({'is_unique': False, 'errors': {'general': _('Only POST requests are allowed.')}},
                        status=405)


def serialize_questions(qs):
    serialized = []
    for q in qs:
        options = {'A': q.A, 'B': q.B, 'C': q.C, 'D': q.D}
        correct_text = options[q.correct_answer]
        shuffled = list(options.items())
        random.shuffle(shuffled)

        shuffled_options = {}
        new_correct = None
        for new_key, (old_key, text) in zip(['A', 'B', 'C', 'D'], shuffled):
            shuffled_options[new_key] = text
            if text == correct_text:
                new_correct = new_key

        serialized.append({
            "question_id": q.id,
            "question": q.question,
            "A": shuffled_options['A'],
            "B": shuffled_options['B'],
            "C": shuffled_options['C'],
            "D": shuffled_options['D'],
            "correct_answer": new_correct
        })
    return serialized


def assign_test_questions(science_field, field_name, languages):
    if science_field.id == 4:
        questions = list(Question.objects.filter(sciences_id=science_field.id).filter(language='uzbek'))
    else:
        questions = list(Question.objects.filter(sciences_id=science_field.id).filter(language=languages))


    random.shuffle(questions)
    selected = questions[:20]

    if len(selected) < 20:
        print(f"{field_name} bo‘yicha test savollari yetarli emas.")
        return None, "Sizga test topshirish uchun ruxsat berilmagan bo'lishi mumkin. Diplomat University qo'llab-quvvatlash xizmatiga murojaat qiling. Telefon: ☎️ +998 88 126 88 88, ☎️ +998 88 124 88 88"
    return serialize_questions(selected), None


def test(request, ap_number):

    application = get_object_or_404(ApplicationForm, application_number=ap_number)

    if not application.test_status:
        print("Test topshirishga ruxsat berilmagan")
        return render(request, 'apply/test.html', {
            'msg': "Sizga test topshirish uchun ruxsat berilmagan bo'lishi mumkin. Diplomat University qo'llab-quvvatlash xizmatiga murojaat qiling. Telefon: ☎️ +998 88 126 88 88, ☎️ +998 88 124 88 88"
        })

    if application.dtm_status:
        print("DTM statusi = True")
        return render(request, 'apply/test.html', {
            'msg': "Sizga test topshirish uchun ruxsat berilmagan bo'lishi mumkin. Diplomat University qo'llab-quvvatlash xizmatiga murojaat qiling. Telefon: ☎️ +998 88 126 88 88, ☎️ +998 88 124 88 88"
        })

    error_msg = None

    if application.additional_documents_status:

        if application.science_is_one:

            if not application.science_two_json:
                print(application.direction_of_education.science_two.id)
                print(application.direction_of_education.science_two.name)
                data, error_msg = assign_test_questions(application.direction_of_education.science_two, "Fan-2", application.language)

                if error_msg:
                    return render(request, 'apply/test.html', {'msg': error_msg})
                application.science_two_json = data

        elif application.science_two:

            if not application.science_is_one_json:
                print(application.direction_of_education.science_is_one.id)
                print(application.direction_of_education.science_is_one.name)
                data, error_msg = assign_test_questions(application.direction_of_education.science_is_one, "Fan-1", application.language)

                if error_msg:
                    return render(request, 'apply/test.html', {'msg': error_msg})
                application.science_is_one_json = data
        else:
            print("Fan sertifikati haqida ma'lumot topilmadi. Iltimos, qo‘llab-quvvatlash xizmatiga murojaat qiling.")
            return render(request, 'apply/test.html', {
                'msg': "Sizga test topshirish uchun ruxsat berilmagan bo'lishi mumkin. Diplomat University qo'llab-quvvatlash xizmatiga murojaat qiling. Telefon: ☎️ +998 88 126 88 88, ☎️ +998 88 124 88 88"
            })
    else:

        if not application.science_is_one_json and not application.science_two_json:

            data1, error1 = assign_test_questions(application.direction_of_education.science_is_one, "Fan-1", application.language)
            print(application.direction_of_education.science_is_one.id)
            print(application.direction_of_education.science_is_one.name)
            data2, error2 = assign_test_questions(application.direction_of_education.science_two, "Fan-2", application.language)
            print(application.direction_of_education.science_two.id)
            print(application.direction_of_education.science_two.name)

            if error1 or error2:
                return render(request, 'apply/test.html', {'msg': error1 or error2})

            application.science_is_one_json = data1
            application.science_two_json = data2

    application.test_status = False

    application.save()

    context = {
        'application': application,
    }

    if application.science_is_one_json and not application.science_is_one :
        context['science_is_one'] = application.science_is_one_json
        context['science_one_name'] = application.direction_of_education.science_is_one.name
        context['science_one_id'] = application.direction_of_education.science_is_one.id

    if application.science_two_json and not application.science_two:
        context['science_two'] = application.science_two_json
        context['science_two_name'] = application.direction_of_education.science_two.name
        context['science_two_id'] = application.direction_of_education.science_two.id

    return render(request, 'apply/test.html', context)


def save_test_results(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            application_number = data.get("application_number")
            user_answers_one = data.get("science_is_one_json", [])
            user_answers_two = data.get("science_two_json", [])

            application = ApplicationForm.objects.get(application_number=application_number)

            questions_one = application.science_is_one_json or []
            questions_two = application.science_two_json or []

            def calculate_score(questions, user_answers, question_ball):
                correct_count = 0
                user_answer_map = {str(item['question_id']): item['user_answer'] for item in user_answers}
                for q in questions:
                    qid = str(q['question_id'])
                    if qid in user_answer_map and q.get('correct_answer') == user_answer_map[qid]:
                        correct_count += question_ball
                return correct_count

            fan1_score = 0
            fan2_score = 0

            if application.additional_documents_status:
                if application.science_is_one:
                    fan1_score = 60
                    fan2_score = calculate_score(questions_two, user_answers_two, 2)
                elif application.science_two:
                    fan1_score = calculate_score(questions_one, user_answers_one, 3)
                    fan2_score = 40
            else:
                fan1_score = calculate_score(questions_one, user_answers_one, 3)
                fan2_score = calculate_score(questions_two, user_answers_two, 2)

            application.science_is_one_user = user_answers_one
            application.science_two_user = user_answers_two
            application.science_is_one_score = fan1_score
            application.science_two_score = fan2_score
            application.rating = fan1_score+fan2_score

            if fan1_score+fan2_score>30:
                application.status = 'approved'
            else:
                application.status = 'rejected'

            application.save()

            return JsonResponse({
                "status": "success",
                "message": "Natijalar saqlandi",
                "fan1_score": fan1_score,
                "fan2_score": fan2_score,
                "rating": fan1_score + fan2_score,

            })


        except ApplicationForm.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Ariza topilmadi"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "POST methodi kerak"}, status=405)




