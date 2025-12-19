from django.db.migrations.operations.base import Operation


class CreateExtension(Operation):
    """
    Create a PostgreSQL extension.

    Usage in migrations:
        operations = [
            CreateExtension('pg_textsearch'),
        ]
    """

    reversible = True

    def __init__(self, name, schema=None):
        self.name = name
        self.schema = schema

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != "postgresql":
            return

        schema_clause = f" SCHEMA {self.schema}" if self.schema else ""
        schema_editor.execute(
            f"CREATE EXTENSION IF NOT EXISTS {self.name}{schema_clause}"
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != "postgresql":
            return

        schema_editor.execute(f"DROP EXTENSION IF EXISTS {self.name}")

    def describe(self):
        return f"Create extension {self.name}"

    @property
    def migration_name_fragment(self):
        return f"create_extension_{self.name}"

    def deconstruct(self):
        kwargs = {"name": self.name}
        if self.schema:
            kwargs["schema"] = self.schema
        return (self.__class__.__qualname__, [], kwargs)


class CreatePgTextsearchExtension(CreateExtension):
    """
    Create the pg_textsearch extension for BM25 full-text search.

    Requires PostgreSQL 17+.

    Usage in migrations:
        operations = [
            CreatePgTextsearchExtension(),
        ]
    """

    def __init__(self, schema=None):
        super().__init__("pg_textsearch", schema=schema)


class CreateBM25Index(Operation):
    """
    Create a BM25 index on a table using pg_textsearch.

    Usage in migrations:
        operations = [
            CreateBM25Index(
                model_name='article',
                name='article_content_bm25',
                fields=['content'],
                text_config='english',
            ),
        ]
    """

    reversible = True

    def __init__(
        self,
        model_name,
        name,
        fields,
        text_config="english",
        k1=1.2,
        b=0.75,
    ):
        self.model_name = model_name
        self.name = name
        self.fields = fields
        self.text_config = text_config
        self.k1 = k1
        self.b = b

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != "postgresql":
            return

        model = to_state.apps.get_model(app_label, self.model_name)
        table = model._meta.db_table

        # Build column list
        columns = []
        for field_name in self.fields:
            field = model._meta.get_field(field_name)
            columns.append(schema_editor.quote_name(field.column))

        columns_sql = ", ".join(columns)

        # Build WITH clause
        with_params = [f"text_config = '{self.text_config}'"]
        if self.k1 != 1.2:
            with_params.append(f"k1 = {self.k1}")
        if self.b != 0.75:
            with_params.append(f"b = {self.b}")

        with_clause = f" WITH ({', '.join(with_params)})"

        sql = (
            f"CREATE INDEX {schema_editor.quote_name(self.name)} "
            f"ON {schema_editor.quote_name(table)} "
            f"USING bm25 ({columns_sql}){with_clause}"
        )
        schema_editor.execute(sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != "postgresql":
            return

        schema_editor.execute(
            f"DROP INDEX IF EXISTS {schema_editor.quote_name(self.name)}"
        )

    def describe(self):
        return f"Create BM25 index {self.name} on {self.model_name}"

    @property
    def migration_name_fragment(self):
        return f"create_bm25_index_{self.name}"

    def deconstruct(self):
        kwargs = {
            "model_name": self.model_name,
            "name": self.name,
            "fields": self.fields,
        }
        if self.text_config != "english":
            kwargs["text_config"] = self.text_config
        if self.k1 != 1.2:
            kwargs["k1"] = self.k1
        if self.b != 0.75:
            kwargs["b"] = self.b
        return (self.__class__.__qualname__, [], kwargs)
