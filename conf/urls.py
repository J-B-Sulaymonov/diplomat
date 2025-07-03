from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from apply import admin_views
from apply.views import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path('upload_question_file/', admin_views.upload_question_file, name='upload_question_file'),

    path('', include('apply.urls')),
    path('set_language/<str:language>/', set_language, name='set_language'),

    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

