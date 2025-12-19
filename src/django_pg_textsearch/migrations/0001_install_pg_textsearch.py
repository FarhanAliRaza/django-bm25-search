"""
Initial migration to install the pg_textsearch extension.

Requires PostgreSQL 17+ with pg_textsearch extension available.
"""

from django.db import migrations

from django_pg_textsearch.operations import CreatePgTextsearchExtension


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        CreatePgTextsearchExtension(),
    ]
