"""
Pytest configuration for django-pg-textsearch tests.
"""

import os
import sys

# Add project root and src to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

import django  # noqa: E402
import pytest  # noqa: E402
from django.conf import settings  # noqa: E402


def pytest_configure():
    """Configure Django settings for tests."""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": os.environ.get("POSTGRES_DB", "django_pg_textsearch_test"),
                    "USER": os.environ.get("POSTGRES_USER", "postgres"),
                    "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
                    "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
                    "PORT": os.environ.get("POSTGRES_PORT", "5432"),
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django_pg_textsearch",
                "tests",
            ],
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            USE_TZ=True,
            SECRET_KEY="test-secret-key",
        )
        django.setup()


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Set up test database."""
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command("migrate", "--run-syncdb", verbosity=0)


@pytest.fixture
def article_factory(db):
    """Factory for creating Article instances."""
    from tests.models import Article

    def create_article(title="Test Article", content="Test content", **kwargs):
        return Article.objects.create(title=title, content=content, **kwargs)

    return create_article
