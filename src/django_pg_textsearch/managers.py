from django.db import models

from .expressions import BM25Score


class BM25SearchQuerySet(models.QuerySet):
    """
    A QuerySet with BM25 full-text search capabilities using pg_textsearch.

    Requires PostgreSQL 17+ with pg_textsearch extension.
    """

    def bm25_search(self, query, field, index_name=None, limit=None):
        """
        Perform a BM25 search using pg_textsearch's <@> operator.

        IMPORTANT: Results are ordered by ascending score (lower = better match).

        Args:
            query: The search query string
            field: The field to search (must have BM25 index)
            index_name: Optional explicit index name
            limit: Optional limit on results

        Returns:
            QuerySet ordered by BM25 relevance
        """
        if not query:
            return self.none()

        score_expr = BM25Score(field, query, index_name=index_name)
        qs = self.annotate(bm25_score=score_expr).order_by("bm25_score")

        if limit:
            qs = qs[:limit]

        return qs

    def bm25_filter(self, query, field, index_name, threshold=-1.0):
        """
        Filter results by BM25 score threshold.

        Args:
            query: The search query string
            field: The field to search
            index_name: The BM25 index name (required for WHERE clause)
            threshold: Score threshold (default -1.0, lower = stricter match)

        Returns:
            Filtered QuerySet
        """
        if not query:
            return self.none()

        return self.extra(
            where=[f'"{field}" <@> to_bm25query(%s, %s) < %s'],
            params=[query, index_name, threshold],
        )


class BM25SearchManager(models.Manager):
    """
    A Django Manager with BM25 full-text search using pg_textsearch.

    Requires PostgreSQL 17+ with pg_textsearch extension.

    Usage:
        class Article(models.Model):
            title = models.CharField(max_length=255)
            content = models.TextField()

            objects = BM25SearchManager()

            class Meta:
                indexes = [
                    BM25Index(fields=['content'], name='article_bm25_idx'),
                ]

        # BM25 search (scores are NEGATIVE, lower = better)
        Article.objects.bm25_search('postgresql', 'content')

        # With explicit index name (required for WHERE filtering)
        Article.objects.bm25_filter('postgresql', 'content', 'article_bm25_idx')
    """

    def get_queryset(self):
        return BM25SearchQuerySet(self.model, using=self._db)

    def bm25_search(self, query, field, index_name=None, limit=None):
        return self.get_queryset().bm25_search(query, field, index_name, limit)

    def bm25_filter(self, query, field, index_name, threshold=-1.0):
        return self.get_queryset().bm25_filter(query, field, index_name, threshold)
