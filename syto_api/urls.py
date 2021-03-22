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
        views.availability_overview_list,
        name="total-availability-list",
    ),
    path(
        f"{API_VERSION_PREFIX}/swagger",
        TemplateView.as_view(template_name=TEMPLATES_DIR / "swagger-ui.html"),
    ),
]
