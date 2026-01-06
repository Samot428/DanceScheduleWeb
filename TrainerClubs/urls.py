from django.urls import path
from . import views

urlpatterns = [
    path('trainer_dashboard/', views.dashboard, name='dashboard'),
    path('add_club/', views.add_club, name='add_club'),
]