import os
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Max

#About
class About(models.Model):
    name = models.CharField(max_length=1000, default="", verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/about', default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Haqida"
        verbose_name_plural = "Haqida"

class VisionAndMission(models.Model):
    name = models.CharField(max_length=1000, default="", verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/mission', default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Maqsad va vazifalar"
        verbose_name_plural = "Maqsad va vazifalar"


class Department(models.Model):
    name = models.CharField(max_length=1000, default="", verbose_name="Nomi")
    img = models.ImageField(upload_to='img/departament', default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kafedra"
        verbose_name_plural = "Kafedra"

class DepartmentTeachers(models.Model):
    type = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Turi")
    name = models.CharField(max_length=1000, default="", verbose_name="FIO")
    phone = models.CharField(max_length=1000, default="", verbose_name="Telefon")
    mail = models.CharField(max_length=1000, default="", verbose_name="Email")
    job_title = models.CharField(max_length=1000, default="", verbose_name="Lavozimi")
    img = models.ImageField(upload_to='img/teachers', default="", )
    short_info = models.CharField(max_length=1000, default="",  verbose_name = "Qizqa izoh")
    info = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kafedra o'qituvchilari"
        verbose_name_plural = "Kafedra o'qituvchilari"

class Management(models.Model):
    name = models.CharField(max_length=1000, default="", verbose_name="FIO")
    phone = models.CharField(max_length=1000, default="", verbose_name="Telefon")
    mail = models.CharField(max_length=1000, default="", verbose_name="Email")
    job_title = models.CharField(max_length=1000, default="", verbose_name="Lavozimi")
    img = models.ImageField(upload_to='img/managment', default="", )
    short_info = models.CharField(max_length=1000, default="",  verbose_name = "Qizqa izoh")
    info = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Boshqaruv"
        verbose_name_plural = "Boshqaruv"


class OurPartners(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    link = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Link")
    img = models.ImageField(upload_to='img/partners', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Xamkorlar"
        verbose_name_plural = "Xamkorlar"

class Banner(models.Model):
    img = models.ImageField(upload_to='img/banner', default="")

    class Meta:
        verbose_name = "Banner rasm"
        verbose_name_plural = "Banner rasm"

#Programs
class Programs(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    img = models.ImageField(upload_to='img/programs', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dasturlar"
        verbose_name_plural = "Dasturlar"

class ProgramDirection(models.Model):
    type = models.ForeignKey(Programs, on_delete=models.CASCADE, verbose_name="Turi")
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/programs/direction', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dasturlar"
        verbose_name_plural = "Dasturlar"

#Admission

class Admission(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/admission', blank=True, null=True)
    order_number = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Qabul"
        verbose_name_plural = "Qabul"

#Student Council
class StudentCouncil(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/admission', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Talabalar kengashi"
        verbose_name_plural = "Talabalar kengashi"

# News
class NewsType(models.Model):
    name = models.CharField(max_length=1000, default="", verbose_name="Nomi")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Yangilik turi"
        verbose_name_plural = "Yangilik turi"


class News(models.Model):
    type = models.ForeignKey(NewsType, on_delete=models.CASCADE, verbose_name="Turi")
    name = models.CharField(max_length=1000, default="", verbose_name="Nomi")
    short_info = models.CharField(max_length=1000, default="", verbose_name="Qisqa iozh")
    info = RichTextUploadingField()
    img_news = models.ImageField(upload_to='img/news', default="")
    views = models.IntegerField( default="0", verbose_name="Ko'rishlar soni")
    status = models.BooleanField(default=False,verbose_name="Slayderni yoqish")
    tg_status = models.BooleanField(default=False,verbose_name="Telegramga chiqarish")
    telegram_message_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangilik"

def news_img_upload_path(instance, filename):
    ext = filename.split('.')[-1]

    last_id = NewsImg.objects.aggregate(Max('id'))['id__max']
    next_id = (last_id or 0) + 1
    filename = f"photo{next_id}.{ext}"
    return os.path.join('img/news', filename)

class NewsImg(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name="Yangilik",related_name='news_images')
    img = models.ImageField(upload_to=news_img_upload_path, default="")

    def __str__(self):
        return self.news.name

    class Meta:
        verbose_name = "Yangilik rasm"
        verbose_name_plural = "Yangilik rasm"

class Fotogalareya(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    img = models.ImageField(upload_to='img/fotogalareya', default="")



    class Meta:
        verbose_name = "Fotogalareya"
        verbose_name_plural = "Fotogalareya"


#Grants And Scholarships
class GrantsAndScholarships(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/GrantsAndScholarships', blank=True, null=True)
    order_number = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grantlar va Stipendiyalar"
        verbose_name_plural = "Grantlar va Stipendiyalar"

#Grants And Scholarships
class Esg(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True, null=True, verbose_name="Nomi")
    info = RichTextUploadingField()
    img = models.ImageField(upload_to='img/GrantsAndScholarships', blank=True, null=True)
    order_number = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brm"
        verbose_name_plural = "Brm"

