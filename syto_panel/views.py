from pathlib import Path

from django.views.generic import TemplateView

from .apps import SytoPanelConfig


class VueJsView(TemplateView):
    template_name = Path(SytoPanelConfig.name) / "index.html"
