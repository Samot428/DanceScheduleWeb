from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'schedule'

urlpatterns = [
    path('schedule_view/', views.schedule_view, name='make_schedule'),
    path('upload_schedule_files/', views.upload_schedule_files, name='upload_schedule_files'),
    path('get_uploaded_files/', views.get_uploaded_files, name='get_uploaded_files'),
    path('delete_uploaded_file/<int:file_id>/', views.delete_uploaded_file, name='delete_uploaded_file'),
    path('create_schedule/', views.create_schedule, name='create_schedule'),

    path('', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)