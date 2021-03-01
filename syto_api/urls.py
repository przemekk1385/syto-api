from django.urls import include, path

from . import views
from .apps import SytoApiConfig

app_name = SytoApiConfig.name
urlpatterns = [
    path("availability", views.availability_list_view, name="availability-list"),
]
