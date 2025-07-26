import os
import sqlite3

class DBConnection:
    def __init__(self):
        self.conn = None
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'clipboard_settings.db')

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn = self.connect()
        cur = conn.cursor()
        cur.executescript(schema_sql)
        conn.commit()
        cur.close() 