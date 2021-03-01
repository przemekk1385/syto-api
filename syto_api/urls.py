from django.urls import include, path

from . import views
from .apps import SytoApiConfig
from .routers import router

app_name = SytoApiConfig.name
urlpatterns = [
    path("", include(router.urls)),
    path("availability", views.AvailabilityView.as_view(), name="availability-list"),
]
