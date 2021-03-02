from django.urls import include, path

from . import views
from .apps import SytoApiConfig
from .routers import router

app_name = SytoApiConfig.name
urlpatterns = [
    path("", include(router.urls)),
    path(
        "availability/",
        views.total_availability_list_view,
        name="total-availability-list",
    ),
]
