import os
import sqlite3

from patterns.singleton.singleton import SingletonMeta

# base de datos en <raiz_del_proyecto>/data/game.db
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "game.db",
)


class DatabaseConnection(metaclass=SingletonMeta):
    """Conexion unica a la base de datos SQLite del juego (patron Singleton).

    Se crea una sola vez la primera vez que se instancia (o que se instancia
    cualquier Repository que la use) y despues siempre se reutiliza la misma
    conexion, evitando abrir el archivo .db mas de una vez.
    """

    def __init__(self, db_path=DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        self._create_tables()

    def _create_tables(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        self.connection.commit()

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()