from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Default redirect/root
    path('', views.couples_groups, name='home'),

    # Calendar main view
    path('calendar/', views.couples_groups, name='calendar_view'),

    # Add/Delete Couple
    path('calendar/add/', views.add_couple, name='add_couple'),
    path('calendar/delete/<int:couple_id>/', views.delete_couple, name='delete_couple'),
    # Inline couple updates
    path('couples/update/<int:couple_id>/', views.update_couple_name, name='update_couple_name'),

    # Add/Delete Trainer
    path('trainers/add/', views.add_trainer, name='add_trainer'), 
    path('trainers/delete/<int:trainer_id>/', views.delete_trainer, name='delete_trainer'),
    # Inline trainer updates
    path('trainers/update/<int:trainer_id>/', views.update_trainer_name, name='update_trainer_name'),
    path('trainers/add_trainer_to_day/', views.add_trainer_to_day, name='add_trainer_to_day'),
    path('trainers/delete_trainer_from_day/<int:trainer_id>', views.delete_trainer_from_day, name='delete_trainer_from_day'),
    path('trainers/update_trainer_time/<int:trainer_id>/', views.update_trainer_time, name='update_trainer_time'),

    # Manage Groups Page + actions
    path('manage_groups/', views.manage_groups, name='manage_groups'),
    path('manage_groups/fragment/', views.manage_groups_fragment, name='manage_groups_fragment'),
    path('manage_groups/add_group/', views.add_group, name='add_group'),
    path('manage_groups/delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('groups/update/<int:group_id>/', views.update_group_name, name='update_group_name'),
    path('couples/move/', views.move_couple, name='move_couple'),

    # Manage Days + actions
    path('manage_days/', views.manage_days, name='manage_days'),
    path('manage_days/fragment/', views.manage_days_fragment, name='manage_days_fragment'),
    path('manage_days/add_day/', views.add_day, name='add_day'),
    path('manage_days/delete_day/<int:day_id>/', views.delete_day, name='delete_day'),
    path('days/update/<int:day_id>/', views.update_day_name, name='update_day_name'),
    path('couples/move_day/', views.move_couple_in_days, name='move_couple_in_days'),
    path('manage_days/remove_couple/<int:couple_id>/', views.remove_couple_from_day, name='remove_couple_from_day'),
    path('days/update_time/<int:day_id>/', views.update_day_time, name='update_day_time'),

    path('days/delete_group_lesson/<int:group_lesson_id>', views.delete_group_lesson, name='delete_group_lesson'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)