import uuid
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
import uuid
import random
import string


class Sciences(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Nomi")
    status = models.BooleanField(default=False, verbose_name="Holati")
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True, )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Muallif",
        default=1
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"


class Question(models.Model):
    ANSWER_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    LANGUAGE_CHOICES = [
        ('uzbek', _("Uzbek")),
        ('russian', _('Russian')),
    ]

    sciences = models.ForeignKey(Sciences, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fan")
    question = models.TextField(verbose_name="Savol matni")
    A = models.TextField(verbose_name="A variant")
    B = models.TextField(verbose_name="B variant")
    C = models.TextField(verbose_name="C variant")
    D = models.TextField(verbose_name="D variant")

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        verbose_name="To'g'ri javob"
    )

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        verbose_name="Test tili"
    )
    status = models.BooleanField(default=True, verbose_name="Holati")
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True, )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Muallif",
        default=1
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"


class Dagree(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Nomi")
    status = models.BooleanField(default=False, verbose_name="Holati")
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True, )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Muallif",
        default=1
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Daraja"
        verbose_name_plural = "Darajalar"


class DirectionOfEducation(models.Model):
    dagree = models.ForeignKey(Dagree, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Daraja",
                               default=1)
    name = models.CharField(max_length=1000, verbose_name="Nomi")
    status = models.BooleanField(default=False, verbose_name="Holati")

    science_is_one = models.ForeignKey(
        Sciences,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Birinchi asosiy fan",
        related_name="primary_directions"
    )
    science_two = models.ForeignKey(
        Sciences,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Ikkinchi asosiy fan",
        related_name="secondary_directions"
    )
    externally = models.BooleanField(default=False, verbose_name="Sirtqi ta'lim")
    personally = models.BooleanField(default=False, verbose_name="Kunduzgi ta'lim")
    remote = models.BooleanField(default=False, verbose_name="Masofaviy ta'lim")
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True, )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Muallif",
        default=1
    )

    def clean(self):
        super().clean()
        if self.science_is_one and self.science_two and self.science_is_one == self.science_two:
            raise ValidationError({
                'science_two': "Ikkinchi fan birinchi fan bilan bir xil bo'lishi mumkin emas."
            })

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim yo'nalishi"
        verbose_name_plural = "Ta'lim yo'nalishlari"


@deconstructible
class FileUploadPath:
    def __init__(self, sub_folder):
        self.sub_folder = sub_folder

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1]
        new_filename = f"{uuid.uuid4()}{ext}"

        return os.path.join(
            'uploads',
            'arizalar',
            str(instance.id or 'yangi'),
            self.sub_folder,
            new_filename
        )

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.sub_folder == other.sub_folder


class Region(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Muallif",
        default=1
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
        ordering = ['name']


class ApplicationForm(models.Model):
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
    ]
    FORM_OF_EDUCATION = [
        ('externally', _("External learning")),
        ('personally', _("Full-time")),
        ('remote', _("Distance learning")),
    ]
    LANGUAGE_CHOICES = [
        ('uzbek', _("Uzbek")),
        ('russian', _('Russian')),
    ]

    STATUS_CHOICES = [
        ('pending', _('New')),
        ('review', _("Under review")),
        ('approved', _('Confirmed')),
        ('rejected', _('Rejected')),
    ]

    phone_validator = RegexValidator(
        regex=r'^\+?998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$',
        message="Telefon raqamini '+998901234567' formatida kiriting."
    )
    passport_validator = RegexValidator(
        regex=r'^[A-Z]{2}\d{7}$',
        message="Pasport seriyasini 'AA1234567' formatida kiriting."
    )
    application_number = models.CharField(max_length=100, verbose_name="Ariza raqami")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Ariza holati"
    )
    test_status = models.BooleanField(default=True)
    surname = models.CharField(max_length=100, verbose_name="Familya")
    first_name = models.CharField(max_length=100, verbose_name="Ism")
    middle_name = models.CharField(max_length=100, verbose_name="Sharif", blank=True)
    phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name="Telefon raqami")
    telegram = models.CharField(max_length=100, verbose_name="Telegram username yoki telefon nomer", blank=True, )

    dagree = models.ForeignKey(
        Dagree,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Daraja",
        default=1
    )
    direction_of_education = models.ForeignKey(
        DirectionOfEducation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Talim yo'nalishi",
        default=1
    )
    form_of_education = models.CharField(max_length=10, choices=FORM_OF_EDUCATION, verbose_name="Ta'lim shakli")
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, verbose_name="Test tili")

    passport = models.CharField(max_length=9, unique=True, validators=[passport_validator],
                                verbose_name="Pasport seriyasi va raqami")
    jshir = models.CharField(max_length=14, verbose_name="JSHIR", unique=True, )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Jinsi")

    address_of_permanent_residence = models.CharField(max_length=500, verbose_name="Doimiy yashash manzili")
    region = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name="Viloyat" )

    photo = models.ImageField(upload_to=FileUploadPath('photos'), verbose_name="Surat (3x4)")
    passport_copy = models.FileField(upload_to=FileUploadPath('passports'), verbose_name="Pasport nusxasi")
    diploma = models.FileField(upload_to=FileUploadPath('diplomas'), verbose_name="Diplom/Shaxodatnoma (ilovasi bilan)")

    dtm_file = models.FileField(upload_to=FileUploadPath('dtm_files'), blank=True, null=True,
                                verbose_name="DTM qaydnomasi (mavjud bo'lsa)")
    dtm_ball = models.FloatField(blank=True, null=True, verbose_name="DTM bali (mavjud bo'lsa)")

    dtm_status = models.BooleanField(default=False, verbose_name="DTM qaydnomasi holati")

    additional_documents = models.FileField(upload_to=FileUploadPath('additional'), blank=True, null=True,
                                            verbose_name="Qo'shimcha hujjatlar")
    additional_documents_status=models.BooleanField(default=False, verbose_name="Qo'shimcha hujjatlar holati")

    science_is_one=models.BooleanField(default=False,verbose_name="Birinchi fan")
    science_two=models.BooleanField(default=False, verbose_name="Ikkinchi fan")
    science_is_one_score = models.IntegerField(max_length=2,default=0, verbose_name="Birinchi fan bahosi", blank=True, null=True)
    science_two_score = models.IntegerField(max_length=2, default=0, verbose_name="Ikkinchi fan bahosi", blank=True, null=True)
    rating = models.CharField(max_length=3,default=0, verbose_name="Umumiy bahosi", blank=True, null=True)

    science_is_one_json = models.JSONField(default=dict, blank=True, null=True, verbose_name="Birinchi fan savollari")
    science_two_json = models.JSONField(default=dict, blank=True, null=True, verbose_name="Ikkinchi fan savollari")
    science_is_one_user = models.JSONField(default=dict, blank=True, null=True, verbose_name="Birinchi fan Foydalanuvchi javoblari")
    science_two_user= models.JSONField(default=dict, blank=True, null=True, verbose_name="Ikkinchi fan Foydalanuvchi javoblari")



    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"{self.surname} {self.first_name}"


    class Meta:
        verbose_name = "Ariza"
        verbose_name_plural = "Arizalar"
        ordering = ['-created_at']


    def generate_uuid(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


    def save(self, *args, **kwargs):
        if self._state.adding:

            if self.additional_documents:
                self.additional_documents_status = True
                self.status = 'pending'
                self.test_status = False
            else:
                self.additional_documents_status = False

            if self.dtm_file or self.dtm_ball is not None:
                self.dtm_status = True
                self.status = 'pending'
                self.test_status = False
            else:
                self.dtm_status = False

        super().save(*args, **kwargs)


