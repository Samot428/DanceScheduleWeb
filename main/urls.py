from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from sheet.views import sheet_view

urlpatterns = [
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/login/", views.custom_login, name="login"),
    path("accounts/logout/", views.custom_logout, name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    # Default redirect/root
    path('', views.couples_groups, name='home'),
    path('trainer/', include('TrainerClubs.urls')),
    path('dancer/', include('DancersClubs.urls')),

    # Calendar main view
    path('club/<int:club_id>/', views.couples_groups, name='calendar_view'),
    path('club/<int:club_id>/sheet', sheet_view, name='sheet'),
    path('', include("sheet.urls")),
    # Add/Delete Couple
    path('club/<int:club_id>/add/', views.add_couple, name='add_couple'),
    path('club/<int:club_id>/delete/<int:couple_id>/', views.delete_couple, name='delete_couple'),
    # Inline couple updates
    path('couples/update/<int:couple_id>/', views.update_couple_name, name='update_couple_name'),
    path('dancers/update/<int:dancer_id>/', views.update_dancer_name, name='update_dancer_name'),

    # Add/Delete Trainer
    path('club/<int:club_id>/trainers/add/', views.add_trainer, name='add_trainer'), 
    path('club/<int:club_id>/trainers/delete/<int:trainer_id>/', views.delete_trainer, name='delete_trainer'),
    # Inline trainer updates
    path('club/<int:club_id>/trainers/update/<int:trainer_id>/', views.update_trainer_name, name='update_trainer_name'),
    path('club/<int:club_id>/trainers/add_trainer_to_day/', views.add_trainer_to_day, name='add_trainer_to_day'),
    path('club/<int:club_id>/trainers/delete_trainer_from_day/<int:trainer_id>', views.delete_trainer_from_day, name='delete_trainer_from_day'),
    path('club/<int:club_id>/trainers/update_trainer_time/<int:trainer_id>/', views.update_trainer_time, name='update_trainer_time'),

    # Manage Groups Page + actions
    path('club/<int:club_id>/manage_groups/', views.manage_groups, name='manage_groups'),
    path('club/<int:club_id>/manage_groups/fragment/', views.manage_groups_fragment, name='manage_groups_fragment'),
    path('club/<int:club_id>/manage_groups/add_group/', views.add_group, name='add_group'),
    path('club/<int:club_id>/manage_groups/delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('club/<int:club_id>/groups/update/<int:group_id>/', views.update_group_name, name='update_group_name'),
    path('couples/move/', views.move_couple, name='move_couple'),

    # Manage Days + actions
    path('club/<int:club_id>/manage_days/', views.manage_days, name='manage_days'),
    path('club/<int:club_id>/manage_days/fragment/', views.manage_days_fragment, name='manage_days_fragment'),
    path('club/<int:club_id>/manage_days/add_day/', views.add_day, name='add_day'),
    path('club/<int:club_id>/manage_days/delete_day/<int:day_id>/', views.delete_day, name='delete_day'),
    path('club/<int:club_id>/days/update/<int:day_id>/', views.update_day_name, name='update_day_name'),
    path('couples/move_day/', views.move_couple_in_days, name='move_couple_in_days'),
    path('club/<int:club_id>/manage_days/remove_couple/<int:couple_id>/', views.remove_couple_from_day, name='remove_couple_from_day'),
    path('club/<int:club_id>/manage_days/remove_dancer/<int:dancer_id>/', views.remove_dancer_from_day, name='remove_dancer_from_day'),
    path('club/<int:club_id>/days/update_time/<int:day_id>/', views.update_day_time, name='update_day_time'),

    path('club/<int:club_id>/days/delete_group_lesson/<int:group_lesson_id>', views.delete_group_lesson, name='delete_group_lesson'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)