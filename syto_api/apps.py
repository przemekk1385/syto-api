from django.apps import AppConfig


class SytoApiConfig(AppConfig):
    name = "syto_api"

    def ready(self):
        from . import signals
