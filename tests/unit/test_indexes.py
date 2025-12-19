"""
Unit tests for indexes module.
"""

from django_pg_textsearch.indexes import BM25Index


class TestBM25Index:
    """Tests for BM25Index class."""

    def test_init_with_defaults(self):
        """Test BM25Index initialization with default values."""
        index = BM25Index(fields=["content"], name="test_idx")

        assert index.fields == ["content"]
        assert index.name == "test_idx"
        assert index.text_config == "english"
        assert index.k1 == 1.2
        assert index.b == 0.75

    def test_init_with_custom_config(self):
        """Test BM25Index with custom text config."""
        index = BM25Index(
            fields=["content"],
            name="test_idx",
            text_config="german",
        )

        assert index.text_config == "german"

    def test_init_with_custom_bm25_params(self):
        """Test BM25Index with custom k1 and b parameters."""
        index = BM25Index(
            fields=["content"],
            name="test_idx",
            k1=1.5,
            b=0.5,
        )

        assert index.k1 == 1.5
        assert index.b == 0.5

    def test_init_with_multiple_fields(self):
        """Test BM25Index with multiple fields."""
        index = BM25Index(
            fields=["title", "content", "summary"],
            name="multi_field_idx",
        )

        assert index.fields == ["title", "content", "summary"]

    def test_deconstruct_default_values(self):
        """Test deconstruct excludes default values."""
        index = BM25Index(fields=["content"], name="test_idx")
        path, args, kwargs = index.deconstruct()

        assert "text_config" not in kwargs
        assert "k1" not in kwargs
        assert "b" not in kwargs

    def test_deconstruct_custom_values(self):
        """Test deconstruct includes custom values."""
        index = BM25Index(
            fields=["content"],
            name="test_idx",
            text_config="french",
            k1=1.8,
            b=0.6,
        )
        path, args, kwargs = index.deconstruct()

        assert kwargs["text_config"] == "french"
        assert kwargs["k1"] == 1.8
        assert kwargs["b"] == 0.6

    def test_suffix(self):
        """Test index suffix."""
        assert BM25Index.suffix == "bm25"
