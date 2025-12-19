"""
Integration tests for BM25 search using pg_textsearch.
Requires PostgreSQL 17+ with pg_textsearch extension.
"""

import pytest
from django.db import connection

from tests.models import Article


@pytest.fixture(scope="session")
def check_pg_textsearch(django_db_setup, django_db_blocker):
    """Check if pg_textsearch extension is available."""
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_textsearch')"
            )
            available = cursor.fetchone()[0]
            if not available:
                pytest.skip("pg_textsearch extension not installed")


@pytest.mark.django_db
class TestBM25Search:
    """Integration tests for BM25 search."""

    @pytest.fixture(autouse=True)
    def setup_articles(self, db):
        """Create test articles."""
        Article.objects.create(
            title="Introduction to PostgreSQL",
            content="PostgreSQL is a powerful open source relational database system.",
        )
        Article.objects.create(
            title="Django Web Framework",
            content="Django is a high-level Python web framework for rapid development.",
        )
        Article.objects.create(
            title="Full-Text Search Guide",
            content="Full-text search enables searching for documents based on content.",
        )
        Article.objects.create(
            title="Database Performance",
            content="Optimizing database queries improves application performance.",
        )

    @pytest.mark.skip(reason="Requires pg_textsearch extension")
    def test_bm25_search_basic(self):
        """Test basic BM25 search."""
        results = Article.objects.bm25_search("postgresql", "content")

        assert results.count() >= 1
        # Results ordered by ascending score (lower = better)
        first = results.first()
        assert first.bm25_score < 0  # Negative scores

    @pytest.mark.skip(reason="Requires pg_textsearch extension")
    def test_bm25_search_with_limit(self):
        """Test BM25 search with limit."""
        results = Article.objects.bm25_search("database", "content", limit=2)

        assert results.count() <= 2

    @pytest.mark.skip(reason="Requires pg_textsearch extension")
    def test_bm25_search_empty_query(self):
        """Test BM25 search with empty query returns nothing."""
        results = Article.objects.bm25_search("", "content")

        assert results.count() == 0

    @pytest.mark.skip(reason="Requires pg_textsearch extension")
    def test_bm25_search_no_results(self):
        """Test BM25 search with no matching results."""
        results = Article.objects.bm25_search("nonexistentterm12345", "content")

        assert results.count() == 0

    @pytest.mark.skip(reason="Requires pg_textsearch extension")
    def test_bm25_filter_with_threshold(self):
        """Test BM25 filter with threshold."""
        results = Article.objects.bm25_filter(
            "database", "content", "article_content_bm25", threshold=-0.5
        )

        # Should filter based on threshold
        assert results.exists()


@pytest.mark.django_db
class TestBM25Score:
    """Integration tests for BM25Score expression."""

    @pytest.fixture(autouse=True)
    def setup_articles(self, db):
        """Create test articles."""
        Article.objects.create(
            title="PostgreSQL Tutorial",
            content="Learn PostgreSQL database management and optimization.",
        )
        Article.objects.create(
            title="MySQL Guide",
            content="MySQL is another popular database system.",
        )

    @pytest.mark.skip(reason="Requires pg_textsearch extension")
    def test_bm25_score_annotation(self):
        """Test BM25Score annotation."""
        from django_pg_textsearch import BM25Score

        results = Article.objects.annotate(
            score=BM25Score("content", "postgresql")
        ).order_by("score")

        assert results.count() >= 1
        first = results.first()
        assert hasattr(first, "score")
        assert first.score < 0  # Negative score


@pytest.mark.django_db
class TestPostgreSQLVersion:
    """Tests for PostgreSQL version checking."""

    def test_postgresql_is_17_or_higher(self):
        """Verify PostgreSQL version is 17+."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            version_num = int(cursor.fetchone()[0])
            major_version = version_num // 10000

        assert major_version >= 17, f"PostgreSQL {major_version} found, need 17+"
