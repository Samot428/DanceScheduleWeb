from django.urls import path
from . import views

urlpatterns = [
    path('trainer_dashboard/', views.dashboard, name='dashboard'),
    path('add_club/', views.add_club, name='add_club'),
    path('delete_club/<int:club_id>/', views.delete_club, name='delete_club'),
    path('update_club/<int:club_id>/', views.update_club, name='update_club'),
    path('club/<int:club_id>/', views.show_club, name='show_club'), 
]