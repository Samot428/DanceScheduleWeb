from django.urls import path
from . import views
urlpatterns = [
    path('dancers_dashboard/', views.dancers_dashboard, name='dancers_dashboard'),
    path('club/<int:club_id>/', views.show_club, name='dancer_show_club'), 
    path('dancers_dashboard/find_club/', views.find_club, name="find_club"),
]