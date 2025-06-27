import json
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from .models import Dagree, DirectionOfEducation, Region, ApplicationForm
from django.core.exceptions import ObjectDoesNotExist
import logging
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

        try:
            # Validation
            required_fields = ['degree', 'education_direction', 'study_form', 'surname',
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
                app_number = f"DU-{new_application.id:06d}"
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
