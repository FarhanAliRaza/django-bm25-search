# django-hawkeye 🎯

Django BM25 full-text search using PostgreSQL [pg_textsearch](https://github.com/timescale/pg_textsearch) - a lightweight Elasticsearch alternative.

## Features

- **Simple API** - Just add a mixin and search with `Article.search("query")`
- **BM25 ranking** - Industry-standard relevance scoring (same as Elasticsearch)
- **No external services** - Uses PostgreSQL 17+ native search
- **RAG-ready** - Use as the retrieval layer for Retrieval Augmented Generation

## Requirements

- PostgreSQL 17+
- pg_textsearch extension
- Django 4.2+
- Python 3.10+

## Installation

```bash
pip install django-hawkeye
```

### PostgreSQL Extension Setup

This library requires the [pg_textsearch](https://github.com/timescale/pg_textsearch) extension installed on your PostgreSQL server:

```bash
# Install build dependencies
apt-get install build-essential git postgresql-server-dev-17

# Clone and build
git clone https://github.com/timescale/pg_textsearch.git
cd pg_textsearch
make && make install
```

The extension is automatically enabled via Django migrations when you run `python manage.py migrate`.

See the [pg_textsearch repository](https://github.com/timescale/pg_textsearch) for detailed installation instructions.

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_hawkeye',
]
```

## Quick Start

### 1. Define your model

```python
from django.db import models
from django_hawkeye import BM25Index, BM25Searchable

class Article(BM25Searchable, models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        indexes = [
            BM25Index(fields=['content'], name='article_bm25_idx'),
        ]
```

### 2. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Search

```python
# Basic search
Article.search("django tutorial")

# With filters
Article.search("web framework").filter(published=True)[:10]

# With score threshold (lower = better match)
Article.search("django").filter(bm25_score__lt=-1.0)
```

## API

### BM25Searchable Mixin

Add to any model to enable `.search()` method:

```python
class Article(BM25Searchable, models.Model):
    ...
```

### BM25Index

```python
BM25Index(
    fields=['content'],
    name='article_bm25_idx',
    text_config='english',  # PostgreSQL text search config
    k1=1.2,                 # Term frequency saturation (0.1-10.0)
    b=0.75,                 # Length normalization (0.0-1.0)
)
```

### Search Methods

```python
# Basic search - returns BM25SearchQuerySet
Article.search("query")

# Chainable with Django QuerySet methods
Article.search("query").filter(author="John")
Article.search("query").exclude(draft=True)
Article.search("query").select_related('author')
Article.search("query")[:10]  # Limit results

# Filter by score threshold
Article.search("query").filter(bm25_score__lt=-1.0)
```

## Advanced Usage

### Override search() method

```python
class Article(BM25Searchable, models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        indexes = [
            BM25Index(fields=['content'], name='article_bm25_idx'),
        ]

    @classmethod
    def search(cls, query, include_title=False):
        """Custom search with optional title filtering."""
        results = super().search(query)
        if include_title:
            results = results.filter(title__icontains=query)
        return results
```

### Direct Expression API

Use `BM25Score` for full control:

```python
from django_hawkeye import BM25Score

# Manual annotation
Article.objects.annotate(
    score=BM25Score('content', 'search query', index_name='article_bm25_idx')
).order_by('score')

# Multi-field weighted search
from django.db.models import F

Article.objects.annotate(
    title_score=BM25Score('title', query, index_name='title_idx'),
    content_score=BM25Score('content', query, index_name='content_idx'),
).annotate(
    combined=F('title_score') * 2 + F('content_score')
).order_by('combined')
```

### Without Mixin

```python
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
```

## Score Semantics

**pg_textsearch returns NEGATIVE scores.** Lower values = better match.

```python
# Correct - ascending order (best matches first)
Article.search("query")  # Already ordered correctly

# Manual ordering
.order_by('bm25_score')  # ✓ Correct
.order_by('-bm25_score') # ✗ Wrong - worst matches first
```

## Why Hawkeye?

| Feature        | Elasticsearch     | django-hawkeye      |
| -------------- | ----------------- | ------------------- |
| Infrastructure | Separate cluster  | Your PostgreSQL     |
| Sync           | Manual index sync | Automatic (native)  |
| Cost           | $$$               | Free                |
| Setup          | Complex           | Add mixin + migrate |
| BM25 ranking   | ✓                 | ✓                   |

## License

MIT

## Links

- [pg_textsearch](https://github.com/timescale/pg_textsearch) - The PostgreSQL extension
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25) - How ranking works
