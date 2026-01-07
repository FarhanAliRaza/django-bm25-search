"""
django-hawkeye
====================

Django integration for PostgreSQL BM25 full-text search using pg_textsearch extension.

Requirements:
    - PostgreSQL 17+
    - pg_textsearch extension (https://github.com/paradedb/pg_textsearch)

Installation:
    pip install django-hawkeye

Links:
    - GitHub: https://github.com/paradedb/pg_textsearch
    - BM25 Algorithm: https://en.wikipedia.org/wiki/Okapi_BM25


Basic Usage
-----------

1. Add 'django_hawkeye' to INSTALLED_APPS and add the index to your model::

    from django_hawkeye import BM25Index, BM25Searchable

    class Article(BM25Searchable, models.Model):
        title = models.CharField(max_length=255)
        content = models.TextField()

        class Meta:
            indexes = [
                BM25Index(fields=['content'], name='article_bm25_idx'),
            ]

2. Run migrations::

    python manage.py makemigrations
    python manage.py migrate

   The pg_textsearch extension is automatically created when the first BM25Index is applied.

3. Search::

    # Basic search
    Article.search('postgresql')

    # With filters
    Article.search('django').filter(published=True)[:10]

    # With threshold (lower score = better match)
    Article.search('query').filter(bm25_score__lt=-1.0)

Note: BM25 scores are NEGATIVE. Lower values indicate better matches.


Advanced Usage
--------------

Override search() method::

    class Article(BM25Searchable, models.Model):
        title = models.CharField(max_length=255)
        content = models.TextField()

        class Meta:
            indexes = [
                BM25Index(fields=['content'], name='article_bm25_idx'),
            ]

        @classmethod
        def search(cls, query, include_title=False):
            '''Custom search with optional title filtering.'''
            results = super().search(query)
            if include_title:
                results = results.filter(title__icontains=query)
            return results

Direct Expression API::

    from django_hawkeye import BM25Score

    # Manual annotation and ordering
    Article.objects.annotate(
        score=BM25Score('content', 'search query', index_name='article_bm25_idx')
    ).order_by('score')

    # Combine with other filters
    Article.objects.annotate(
        bm25_score=BM25Score('content', query, index_name='idx'),
    ).filter(
        bm25_score__lt=-1.0,
        created_at__gte=last_week,
    ).order_by('bm25_score')

Multi-field weighted search::

    from django.db.models import F
    from django_hawkeye import BM25Score

    Article.objects.annotate(
        title_score=BM25Score('title', query, index_name='title_idx'),
        content_score=BM25Score('content', query, index_name='content_idx'),
    ).annotate(
        combined=F('title_score') * 2 + F('content_score')
    ).order_by('combined')

Without mixin (expressions only)::

    from django_hawkeye import BM25Index, BM25Score

    class Article(models.Model):
        content = models.TextField()

        class Meta:
            indexes = [
                BM25Index(fields=['content'], name='article_bm25_idx'),
            ]

        @classmethod
        def search(cls, query):
            return cls.objects.annotate(
                score=BM25Score('content', query, index_name='article_bm25_idx')
            ).filter(score__lt=0).order_by('score')


API Reference
-------------

Classes:
    BM25Searchable
        Mixin that adds search() classmethod to models.

    BM25Index
        Django Index for creating BM25 indexes in migrations.

    BM25SearchQuerySet
        QuerySet-like wrapper returned by search().

    BM25Score
        Django Expression for BM25 scoring in annotations.

    BM25Query
        Low-level expression for to_bm25query() function.

    BM25Match
        Filter expression for BM25 threshold matching.

Functions:
    is_pg_textsearch_available()
        Check if pg_textsearch extension is installed.

    get_postgresql_version()
        Get PostgreSQL major version number.

Migration Operations:
    CreatePgTextsearchExtension
        Create pg_textsearch extension in migrations.

    CreateBM25Index
        Manually create BM25 index in migrations.
"""

__version__ = "0.4.0"

from .checks import get_postgresql_version, is_pg_textsearch_available
from .expressions import BM25Match, BM25Query, BM25Score
from .indexes import BM25Index
from .mixins import BM25Searchable
from .operations import CreateBM25Index, CreateExtension, CreatePgTextsearchExtension
from .search import BM25SearchQuerySet

__all__ = [
    "__version__",
    # Mixin (recommended)
    "BM25Searchable",
    # Index
    "BM25Index",
    # Search QuerySet
    "BM25SearchQuerySet",
    # Expressions (advanced)
    "BM25Match",
    "BM25Query",
    "BM25Score",
    # Migration Operations
    "CreateBM25Index",
    "CreateExtension",
    "CreatePgTextsearchExtension",
    # Utilities
    "get_postgresql_version",
    "is_pg_textsearch_available",
]
