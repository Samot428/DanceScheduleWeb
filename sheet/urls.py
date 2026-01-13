from django.urls import path
from . import views

urlpatterns = [
    path("dashboard-redirect/", views.dashboard_redirect, name="dashboard_redirect"),
    path("club/<int:club_id>/sheet/", views.sheet_view, name="sheet_view"),
    path("club-redirect/<int:club_id>/", views.club_redirect, name="club_redirect"),
]
