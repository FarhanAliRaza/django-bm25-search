from django.db.models import Index


class BM25Index(Index):
    """
    A Django index class for creating BM25 full-text search indexes using pg_textsearch.

    Requires: PostgreSQL 17+ with pg_textsearch extension.

    Usage:
        class Article(models.Model):
            content = models.TextField()

            class Meta:
                indexes = [
                    BM25Index(fields=['content'], text_config='english', name='article_bm25_idx'),
                ]

    The index is created as:
        CREATE INDEX article_bm25_idx ON article USING bm25(content) WITH (text_config='english');
    """

    suffix = "bm25"

    def __init__(
        self,
        *expressions,
        fields=(),
        text_config="english",
        k1=1.2,
        b=0.75,
        name=None,
        db_tablespace=None,
        opclasses=(),
        condition=None,
        include=None,
    ):
        self.text_config = text_config
        self.k1 = k1
        self.b = b
        super().__init__(
            *expressions,
            fields=fields,
            name=name,
            db_tablespace=db_tablespace,
            opclasses=opclasses,
            condition=condition,
            include=include,
        )

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        if self.text_config != "english":
            kwargs["text_config"] = self.text_config
        if self.k1 != 1.2:
            kwargs["k1"] = self.k1
        if self.b != 0.75:
            kwargs["b"] = self.b
        return path, args, kwargs

    def create_sql(self, model, schema_editor, using="", **kwargs):
        """
        Generate the SQL to create a BM25 index.

        pg_textsearch syntax:
            CREATE INDEX idx_name ON table USING bm25(column) WITH (text_config='english');
        """
        table = model._meta.db_table
        columns = [
            model._meta.get_field(field_name).column for field_name in self.fields
        ]

        # pg_textsearch expects raw column names
        columns_sql = ", ".join(schema_editor.quote_name(col) for col in columns)

        # Build WITH clause for BM25 parameters
        with_params = [f"text_config = '{self.text_config}'"]
        if self.k1 != 1.2:
            with_params.append(f"k1 = {self.k1}")
        if self.b != 0.75:
            with_params.append(f"b = {self.b}")

        with_clause = f" WITH ({', '.join(with_params)})"

        index_name = self.name or f"{table}_{self.suffix}"

        sql = (
            f"CREATE INDEX {schema_editor.quote_name(index_name)} "
            f"ON {schema_editor.quote_name(table)} "
            f"USING bm25 ({columns_sql}){with_clause}"
        )

        return sql

    def remove_sql(self, model, schema_editor, **kwargs):
        """Generate SQL to drop the index."""
        index_name = self.name or f"{model._meta.db_table}_{self.suffix}"
        return f"DROP INDEX IF EXISTS {schema_editor.quote_name(index_name)}"
