from modeltranslation.admin import TranslationAdmin
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resources import QuestionResource
from apply.models import Sciences, Question, Dagree, DirectionOfEducation, Region, ApplicationForm


@admin.register(Sciences)
class SciencesAdmin(TranslationAdmin):
    list_display = ('name', 'status', 'author', 'created_at')

    list_editable = ('status',)

    search_fields = ('name',)

    list_filter = ('status', 'created_at')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Dagree)
class DagreeAdmin(TranslationAdmin):
    list_display = ('name', 'status', 'author', 'created_at')

    list_editable = ('status',)

    search_fields = ('name',)

    list_filter = ('status', 'created_at')

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(DirectionOfEducation)
class DirectionOfEducationAdmin(TranslationAdmin):
    list_display = (
        'name',
        'dagree',
        'science_is_one',
        'science_two',
        'status',
        'externally',
        'personally',
        'remote',
        'author'
    )

    list_editable = (
        'status',
        'externally',
        'personally',
        'remote'
    )

    search_fields = (
        'name',
        'dagree__name',
        'author__username'
    )

    list_filter = (
        'status',
        'dagree',
        'externally',
        'personally',
        'remote'
    )

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Region)
class RegionAdmin(TranslationAdmin):
    list_display = ('name',  'author', 'created_at')

    search_fields = ('name',)

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource

    list_display = ('question', 'A', 'B', 'C', 'D', 'correct_answer', 'sciences', 'status', 'language',)
    list_editable = ('status',)
    list_filter = ('sciences', 'language', 'status',)
    search_fields = ('question', 'sciences__name')


@admin.register(ApplicationForm)
class ApplicationFormAdmin(admin.ModelAdmin):
    list_display = (
        'application_number',
        'get_full_name',
        'phone',
        'dagree',
        'direction_of_education',
        'form_of_education',
        'language',
        'created_at',
        'status',
    )
    list_editable = ('status',)

    list_filter = (
        'dagree',
        'direction_of_education',
        'form_of_education',
        'language',
        'status',
        'region',
        'created_at',
    )

    search_fields = (
        'application_number',
        'surname',
        'first_name',
        'passport',
        'phone',
        'jshir',
    )

    list_per_page = 20

    # fieldsets = (
    #     ('Ariza ma\'lumotlari', {
    #         'fields': (
    #         'application_number', 'status', 'dagree', 'direction_of_education', 'form_of_education', 'language')
    #     }),
    #     ('Abituriyentning shaxsiy ma\'lumotlari', {
    #         'fields': ('surname', 'first_name', 'middle_name', 'gender', 'phone', 'telegram')
    #     }),
    #     ('Pasport va manzil ma\'lumotlari', {
    #         'fields': ('passport', 'jshir', 'region', 'address_of_permanent_residence')
    #     }),
    #     ('Yuklanadigan hujjatlar', {
    #         'fields': ('photo', 'get_photo_preview', 'passport_copy', 'diploma', 'additional_documents')
    #     }),
    #     ('DTM ma\'lumotlari (mavjud bo\'lsa)', {
    #         'classes': ('collapse',),
    #         'fields': ('dtm_ball', 'dtm_file')
    #     }),
    #     ('Shartnomalar', {
    #         'classes': ('collapse',),
    #         'fields': ('bilateral_contract', 'tripartite_contract')
    #     }),
    #     ('Tizim ma\'lumotlari', {
    #         'fields': ('created_at', 'updated_at')
    #     })
    # )

    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return f"{obj.surname} {obj.first_name} {obj.middle_name or ''}".strip()

    get_full_name.short_description = "Abituriyent F.I.SH."
    get_full_name.admin_order_field = 'surname'  # Familya bo'yicha saralash



admin.site.register(Question, QuestionAdmin)
# admin.site.register(Dagree)
# admin.site.register(DirectionOfEducation)
# admin.site.register(Region)
# admin.site.register(ApplicationForm)
