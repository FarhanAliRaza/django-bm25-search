"""
Test models for django-pg-textsearch.
"""

from django.db import models

from django_pg_textsearch import BM25Index, BM25SearchManager


class Article(models.Model):
    """Test model with BM25 search capabilities."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    objects = BM25SearchManager()

    class Meta:
        app_label = "tests"
        indexes = [
            BM25Index(fields=["content"], name="article_content_bm25"),
        ]

    def __str__(self):
        return self.title
