"""
django-pg-textsearch: Django integration for pg_textsearch BM25 full-text search.

Requires PostgreSQL 17+ with pg_textsearch extension.
https://github.com/timescale/pg_textsearch

Usage:
    from django_pg_textsearch import BM25Index, BM25SearchManager

    class Article(models.Model):
        content = models.TextField()
        objects = BM25SearchManager()

        class Meta:
            indexes = [
                BM25Index(fields=['content'], name='article_bm25_idx'),
            ]

    # BM25 search (scores are NEGATIVE, lower = better)
    Article.objects.bm25_search('postgresql', 'content')
"""

__version__ = "0.1.0"

from .checks import get_postgresql_version, is_pg_textsearch_available
from .expressions import BM25Match, BM25Query, BM25Score
from .indexes import BM25Index
from .managers import BM25SearchManager, BM25SearchQuerySet
from .operations import CreateBM25Index, CreateExtension, CreatePgTextsearchExtension

__all__ = [
    "__version__",
    # Index
    "BM25Index",
    # Expressions
    "BM25Match",
    "BM25Query",
    "BM25Score",
    # Managers
    "BM25SearchManager",
    "BM25SearchQuerySet",
    # Operations
    "CreateBM25Index",
    "CreateExtension",
    "CreatePgTextsearchExtension",
    # Checks
    "get_postgresql_version",
    "is_pg_textsearch_available",
]

default_app_config = "django_pg_textsearch.apps.DjangoPgTextsearchConfig"
