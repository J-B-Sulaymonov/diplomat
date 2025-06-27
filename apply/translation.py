from modeltranslation.translator import register, TranslationOptions
from apply.models import Sciences,Dagree,DirectionOfEducation,Region


@register(Dagree)
class DagreeTrans(TranslationOptions):
    fields = ('name',)


# @register(Question)
# class QuestionTrans(TranslationOptions):
#     fields = ('question','A','B','C','D')

@register(Sciences)
class SciencesTrans(TranslationOptions):
    fields = ('name',)

@register(DirectionOfEducation)
class DirectionOfEducationTrans(TranslationOptions):
    fields = ('name',)

@register(Region)
class RegionTrans(TranslationOptions):
    fields = ('name',)

# @register(ApplicationForm)
# class ApplicationFormTrans(TranslationOptions):
#     fields = ('name',)
#

