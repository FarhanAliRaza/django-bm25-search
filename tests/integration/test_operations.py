"""
Integration tests for migration operations.
Requires PostgreSQL 17+.
"""

import pytest
from django.db import connection


@pytest.mark.django_db
class TestPostgreSQLSetup:
    """Tests for PostgreSQL setup and version."""

    def test_postgresql_version(self):
        """Test PostgreSQL version is 17+."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            version_num = int(cursor.fetchone()[0])
            major_version = version_num // 10000

        assert major_version >= 17

    def test_can_execute_sql(self):
        """Test basic SQL execution works."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]

        assert result == 1


@pytest.mark.django_db
class TestCreateExtensionOperation:
    """Tests for CreateExtension operation."""

    def test_create_extension_executes(self):
        """Test extension creation doesn't error."""
        from django_pg_textsearch.operations import CreateExtension

        # Try to create a common extension that exists
        op = CreateExtension("plpgsql")

        with connection.schema_editor() as schema_editor:
            # This should not raise (plpgsql is always installed)
            op.database_forwards("tests", schema_editor, None, None)


@pytest.mark.django_db
class TestPgTextsearchExtension:
    """Tests for pg_textsearch extension."""

    @pytest.mark.skip(reason="pg_textsearch must be installed separately")
    def test_pg_textsearch_available(self):
        """Test pg_textsearch extension is available."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'pg_textsearch')"
            )
            available = cursor.fetchone()[0]

        assert available, "pg_textsearch extension not available"

    @pytest.mark.skip(reason="pg_textsearch must be installed separately")
    def test_pg_textsearch_installed(self):
        """Test pg_textsearch extension is installed."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_textsearch')"
            )
            installed = cursor.fetchone()[0]

        assert installed, "pg_textsearch extension not installed"

    @pytest.mark.skip(reason="pg_textsearch must be installed separately")
    def test_bm25_index_method_exists(self):
        """Test bm25 index method is available."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_am WHERE amname = 'bm25')")
            exists = cursor.fetchone()[0]

        assert exists, "bm25 index method not available"

    @pytest.mark.skip(reason="pg_textsearch must be installed separately")
    def test_to_bm25query_function_exists(self):
        """Test to_bm25query function exists."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'to_bm25query')"
            )
            exists = cursor.fetchone()[0]

        assert exists, "to_bm25query function not available"
