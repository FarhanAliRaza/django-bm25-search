"""
Unit tests for expressions module.
Tests only pg_textsearch specific expressions.
"""

from django_pg_textsearch.expressions import (
    BM25Match,
    BM25Query,
    BM25Score,
)


class TestBM25Query:
    """Tests for BM25Query expression (pg_textsearch)."""

    def test_init_simple(self):
        """Test BM25Query initialization without index name."""
        query = BM25Query("search terms")

        assert query.query == "search terms"
        assert query.index_name is None

    def test_init_with_index_name(self):
        """Test BM25Query with explicit index name."""
        query = BM25Query("search terms", index_name="article_bm25_idx")

        assert query.query == "search terms"
        assert query.index_name == "article_bm25_idx"

    def test_repr_simple(self):
        """Test BM25Query string representation."""
        query = BM25Query("test")

        assert repr(query) == "BM25Query('test')"

    def test_repr_with_index(self):
        """Test BM25Query repr with index name."""
        query = BM25Query("test", index_name="idx")

        assert repr(query) == "BM25Query('test', index_name='idx')"


class TestBM25Score:
    """Tests for BM25Score expression (pg_textsearch)."""

    def test_init(self):
        """Test BM25Score initialization."""
        score = BM25Score("content", "search query")

        assert score.field_name == "content"
        assert score.query == "search query"
        assert score.index_name is None

    def test_init_with_index_name(self):
        """Test BM25Score with explicit index name."""
        score = BM25Score("content", "query", index_name="article_bm25_idx")

        assert score.index_name == "article_bm25_idx"

    def test_repr(self):
        """Test BM25Score string representation."""
        score = BM25Score("content", "query")

        assert repr(score) == "BM25Score('content', 'query')"


class TestBM25Match:
    """Tests for BM25Match expression (pg_textsearch)."""

    def test_init(self):
        """Test BM25Match initialization."""
        match = BM25Match("content", "search query", "article_bm25_idx")

        assert match.field_name == "content"
        assert match.query == "search query"
        assert match.index_name == "article_bm25_idx"
        assert match.threshold == -1.0

    def test_init_custom_threshold(self):
        """Test BM25Match with custom threshold."""
        match = BM25Match("content", "query", "idx", threshold=-2.0)

        assert match.threshold == -2.0
