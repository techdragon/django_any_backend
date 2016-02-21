from .features import DatabaseFeatures
from .creation import DatabaseCreation
from .database import Database
from .schema import DatabaseSchemaEditor
from .introspection import DatabaseIntrospection
from django.db.backends.base.base import BaseDatabaseWrapper
from django.utils.module_loading import import_string
from operations import DatabaseOperations
from importlib import import_module
from cursor import Cursor

class DatabaseWrapper(BaseDatabaseWrapper):
    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor
    is_non_db = True
    default_compiler = 'any_backend.backends.compiler'

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.db_config = args[0]
        compiler_module = self.db_config.get('COMPILER', None) or self.default_compiler
        self._cache = import_module(compiler_module)
        self.ops = DatabaseOperations(self, cache=self._cache)
        self.creation = DatabaseCreation(self)
        self.features = DatabaseFeatures(self)
        self.introspection = DatabaseIntrospection(self)
        client_class = self.db_config['CLIENT']
        client_class = import_string(client_class)
        self.client = client_class(self.create_cursor(), self.db_config)

    def create_cursor(self):
        return Cursor()

    def get_connection_params(self):
        return{'connection': self.db_config}

    def get_new_connection(self, conn_params):
        self.client.setup(self.db_config)
        return self.client

    def is_usable(self):
        return self.connection.check()

    def init_connection_state(self):
        pass

    def _set_autocommit(self, autocommit):
        pass