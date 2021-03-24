from django.urls import path

from . import views
from .apps import SytoPanelConfig

app_name = SytoPanelConfig.name
urlpatterns = [
    path("", views.VueJsView.as_view(), name="index"),
]
