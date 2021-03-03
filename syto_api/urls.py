from pathlib import Path

from django.urls import include, path
from django.views.generic import TemplateView

from . import views
from .apps import SytoApiConfig
from .routers import router

API_VERSION_PREFIX = "v1"
TEMPLATES_DIR = Path(SytoApiConfig.name)

app_name = SytoApiConfig.name
urlpatterns = [
    path(f"{API_VERSION_PREFIX}/", include(router.urls)),
    path(
        f"{API_VERSION_PREFIX}/availability/",
        views.total_availability_list_view,
        name="total-availability-list",
    ),
    path(
        "swagger", TemplateView.as_view(template_name=TEMPLATES_DIR / "swagger-ui.html")
    ),
]
