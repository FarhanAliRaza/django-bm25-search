# django-pg-textsearch

Django integration for [pg_textsearch](https://github.com/timescale/pg_textsearch) - BM25 full-text search for PostgreSQL.

## Requirements

- PostgreSQL 17+
- pg_textsearch extension
- Django 5.0+
- Python 3.10+

## Installation

```bash
uv add django-pg-textsearch
# or
pip install django-pg-textsearch
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_pg_textsearch',
]
```

## Quick Start

### 1. Run migrations

The extension is installed automatically when you run migrations:

```bash
python manage.py migrate
```

### 2. Define your model with BM25 index

```python
from django.db import models
from django_pg_textsearch import BM25Index, BM25SearchManager

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    objects = BM25SearchManager()

    class Meta:
        indexes = [
            BM25Index(fields=['content'], name='article_bm25_idx'),
        ]
```

### 3. Search

```python
# BM25 search - scores are NEGATIVE (lower = better match)
results = Article.objects.bm25_search('django tutorial', 'content')

# With limit
results = Article.objects.bm25_search('web framework', 'content', limit=10)

# Filter by score threshold
results = Article.objects.bm25_filter(
    'django tutorial',
    'content',
    'article_bm25_idx',  # index name required
    threshold=-1.0
)
```

### Manual scoring

```python
from django_pg_textsearch import BM25Score

Article.objects.annotate(
    score=BM25Score('content', 'search query')
).order_by('score')  # ASC because lower = better!
```

## API

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

### Manager Methods

| Method | Description |
|--------|-------------|
| `bm25_search(query, field, index_name=None, limit=None)` | Search with BM25 ranking |
| `bm25_filter(query, field, index_name, threshold=-1.0)` | Filter by score threshold |

### Expressions

| Expression | Description |
|------------|-------------|
| `BM25Score(field, query)` | Annotate with BM25 score |
| `BM25Query(query, index_name=None)` | Create a BM25 query |
| `BM25Match(field, query, index_name, threshold)` | Filter expression |

## Score Semantics

**pg_textsearch returns NEGATIVE scores.** Lower values = better match.

```python
# Correct - ascending order
.order_by('score')

# Wrong - would put worst matches first
.order_by('-score')
```

## License

MIT
