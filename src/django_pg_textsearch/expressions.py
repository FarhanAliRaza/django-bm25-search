from django.db.models import Expression, Field, FloatField


class BM25Query(Expression):
    """
    Creates a BM25 query using pg_textsearch's to_bm25query function.

    Usage:
        # For ORDER BY (auto-detects index):
        Article.objects.order_by(BM25Score('content', 'search terms'))

        # For WHERE clause (requires index name):
        Article.objects.filter(
            BM25Match('content', 'search terms', index_name='article_bm25_idx') < -1.0
        )
    """

    def __init__(self, query, index_name=None):
        """
        Args:
            query: The search query string
            index_name: Optional index name for WHERE clause usage
        """
        self.query = query
        self.index_name = index_name
        super().__init__()

    def __repr__(self):
        if self.index_name:
            return f"BM25Query({self.query!r}, index_name={self.index_name!r})"
        return f"BM25Query({self.query!r})"

    def as_sql(self, compiler, connection):
        if self.index_name:
            return "to_bm25query(%s, %s)", [self.query, self.index_name]
        else:
            return "to_bm25query(%s)", [self.query]

    def resolve_expression(
        self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False
    ):
        return self

    @property
    def output_field(self):
        return Field()


class BM25Score(Expression):
    """
    Calculate BM25 relevance score using pg_textsearch's <@> operator.

    IMPORTANT: pg_textsearch returns NEGATIVE scores. Lower values = better match.
    Use .order_by('score') NOT .order_by('-score')!

    Usage:
        Article.objects.annotate(
            score=BM25Score('content', 'search query')
        ).order_by('score')  # Note: ascending order!
    """

    output_field = FloatField()

    def __init__(self, field_name, query, index_name=None, **extra):
        """
        Args:
            field_name: The text field to search in (must have BM25 index)
            query: The search query string
            index_name: Optional index name (required for WHERE clause)
        """
        self.field_name = field_name
        self.query = query
        self.index_name = index_name
        super().__init__(**extra)

    def __repr__(self):
        return f"BM25Score({self.field_name!r}, {self.query!r})"

    def resolve_expression(
        self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False
    ):
        return self

    def as_sql(self, compiler, connection):
        if self.index_name:
            return (
                f'"{self.field_name}" <@> to_bm25query(%s, %s)',
                [self.query, self.index_name],
            )
        else:
            return f'"{self.field_name}" <@> to_bm25query(%s)', [self.query]


class BM25Match(Expression):
    """
    Filter expression for BM25 search matches.

    Usage:
        Article.objects.filter(
            BM25Match('content', 'search query', index_name='article_bm25_idx', threshold=-1.0)
        )
    """

    def __init__(self, field_name, query, index_name, threshold=-1.0):
        """
        Args:
            field_name: The text field to search
            query: The search query string
            index_name: The BM25 index name (required)
            threshold: Score threshold (default -1.0, lower = stricter)
        """
        self.field_name = field_name
        self.query = query
        self.index_name = index_name
        self.threshold = threshold
        super().__init__()

    def resolve_expression(
        self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False
    ):
        return self

    def as_sql(self, compiler, connection):
        return (
            f'"{self.field_name}" <@> to_bm25query(%s, %s) < %s',
            [self.query, self.index_name, self.threshold],
        )
