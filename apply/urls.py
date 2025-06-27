from django.urls import path
from apply import views


urlpatterns = [
    path('', views.application_form_view, name='application_form'),
    path('ajax/get-directions/<int:degree_id>/', views.get_directions, name='ajax_get_directions'),
    path('ajax/get-study-forms/<int:direction_id>/', views.get_study_forms, name='ajax_get_study_forms'),
    path('api/check-uniqueness/', views.check_uniqueness, name='check_uniqueness'),
    path('check-status/', views.check_application_status, name='check_application_status'),

]