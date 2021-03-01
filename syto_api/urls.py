from django.urls import path

from . import views
from .apps import SytoApiConfig

app_name = SytoApiConfig.name
urlpatterns = [
    path("availability", views.AvailabilityView.as_view(), name="availability-list"),
]
