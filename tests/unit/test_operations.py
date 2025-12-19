"""
Unit tests for operations module.
"""

from django_pg_textsearch.operations import (
    CreateBM25Index,
    CreateExtension,
    CreatePgTextsearchExtension,
)


class TestCreateExtension:
    """Tests for CreateExtension operation."""

    def test_init(self):
        """Test CreateExtension initialization."""
        op = CreateExtension("pg_textsearch")

        assert op.name == "pg_textsearch"
        assert op.schema is None

    def test_init_with_schema(self):
        """Test CreateExtension with schema."""
        op = CreateExtension("pg_textsearch", schema="public")

        assert op.name == "pg_textsearch"
        assert op.schema == "public"

    def test_reversible(self):
        """Test that operation is reversible."""
        op = CreateExtension("pg_textsearch")

        assert op.reversible is True

    def test_describe(self):
        """Test describe output."""
        op = CreateExtension("pg_textsearch")

        assert op.describe() == "Create extension pg_textsearch"

    def test_migration_name_fragment(self):
        """Test migration name fragment."""
        op = CreateExtension("pg_textsearch")

        assert op.migration_name_fragment == "create_extension_pg_textsearch"

    def test_deconstruct(self):
        """Test deconstruct."""
        op = CreateExtension("pg_textsearch", schema="public")
        path, args, kwargs = op.deconstruct()

        assert kwargs["name"] == "pg_textsearch"
        assert kwargs["schema"] == "public"


class TestCreatePgTextsearchExtension:
    """Tests for CreatePgTextsearchExtension operation."""

    def test_init(self):
        """Test initialization creates pg_textsearch extension."""
        op = CreatePgTextsearchExtension()

        assert op.name == "pg_textsearch"


class TestCreateBM25Index:
    """Tests for CreateBM25Index operation."""

    def test_init(self):
        """Test CreateBM25Index initialization."""
        op = CreateBM25Index(
            model_name="article",
            name="article_bm25_idx",
            fields=["content"],
        )

        assert op.model_name == "article"
        assert op.name == "article_bm25_idx"
        assert op.fields == ["content"]
        assert op.text_config == "english"
        assert op.k1 == 1.2
        assert op.b == 0.75

    def test_init_with_custom_params(self):
        """Test CreateBM25Index with custom parameters."""
        op = CreateBM25Index(
            model_name="article",
            name="article_bm25_idx",
            fields=["title", "content"],
            text_config="german",
            k1=1.5,
            b=0.6,
        )

        assert op.fields == ["title", "content"]
        assert op.text_config == "german"
        assert op.k1 == 1.5
        assert op.b == 0.6

    def test_reversible(self):
        """Test that operation is reversible."""
        op = CreateBM25Index(
            model_name="article",
            name="idx",
            fields=["content"],
        )

        assert op.reversible is True

    def test_describe(self):
        """Test describe output."""
        op = CreateBM25Index(
            model_name="article",
            name="article_bm25_idx",
            fields=["content"],
        )

        assert op.describe() == "Create BM25 index article_bm25_idx on article"

    def test_deconstruct_default_values(self):
        """Test deconstruct excludes default values."""
        op = CreateBM25Index(
            model_name="article",
            name="idx",
            fields=["content"],
        )
        path, args, kwargs = op.deconstruct()

        assert "text_config" not in kwargs
        assert "k1" not in kwargs
        assert "b" not in kwargs

    def test_deconstruct_custom_values(self):
        """Test deconstruct includes custom values."""
        op = CreateBM25Index(
            model_name="article",
            name="idx",
            fields=["content"],
            text_config="french",
            k1=1.8,
            b=0.5,
        )
        path, args, kwargs = op.deconstruct()

        assert kwargs["text_config"] == "french"
        assert kwargs["k1"] == 1.8
        assert kwargs["b"] == 0.5
