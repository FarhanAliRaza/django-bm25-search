from django.apps import AppConfig


class DjangoPgTextsearchConfig(AppConfig):
    name = "django_pg_textsearch"
    verbose_name = "Django PG Textsearch"

    def ready(self):
        from . import checks  # noqa: F401
