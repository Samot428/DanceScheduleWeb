from django.urls import path
from . import views

urlpatterns = [
    path('trainer_dashboard/', views.dashboard, name='dashboard'),
    path('add_club/', views.add_club, name='add_club'),
    path('delete_club/<int:club_id>/', views.delete_club, name='delete_club'),
    path('update_club/<int:club_id>/', views.update_club, name='update_club'),
    path('club/<int:club_id>/', views.show_club, name='show_club'), 
    path('club/trainer_view/<int:club_id>/', views.show_not_trainer_club, name="show_not_trainer_club"),
    path('club/trainer_view/<int:club_id>/add_trainer_to_day', views.add_trainer_to_day, name='add_trainer_to_day_by_trainer'),
    path('club/trainer_view/<int:club_id>/update_trainer_time/<int:trainer_id>/', views.update_trainer_time, name='update_trainer_time_by_trainer'),
]