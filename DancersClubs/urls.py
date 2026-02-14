from django.urls import path
from . import views
urlpatterns = [
    path('dancers_dashboard/', views.dancers_dashboard, name='dancers_dashboard'),
    path('club/<int:club_id>/', views.show_club, name='dancer_show_club'), 
    path('dancers_dashboard/find_club/', views.find_club, name="find_club"),
    path('club/<int:club_id>/add_couple', views.add_couple, name="add_couple_by_dancer"),
    path('club/<int:club_id>/delete_couple/<int:couple_id>', views.delete_couple, name="delete_couple_by_dancer"),
]