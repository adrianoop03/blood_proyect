from database.connection import DatabaseConnection


class ScoreRepository:
    """Encapsula todo el acceso SQL a la tabla 'scores' (patron Repository).

    El resto del juego (pantallas de UI, main.py, etc.) nunca escribe SQL
    directamente: solo llama a estos metodos. Si el dia de mañana cambia el
    motor de base de datos, alcanza con reescribir esta clase.
    """

    def __init__(self):
        self.db = DatabaseConnection()

    def save_score(self, player_name, score):
        """Guarda un puntaje nuevo en el ranking."""
        name = (player_name or "").strip()[:20] or "Jugador"

        cursor = self.db.get_cursor()
        cursor.execute(
            "INSERT INTO scores (player_name, score) VALUES (?, ?)",
            (name, int(score)),
        )
        self.db.commit()

    def get_top_scores(self, limit=10):
        """Devuelve los mejores puntajes, de mayor a menor."""
        cursor = self.db.get_cursor()
        cursor.execute(
            """
            SELECT player_name, score, created_at
            FROM scores
            ORDER BY score DESC, created_at ASC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()

    def clear_scores(self):
        """Borra todo el ranking (util para testing/debug)."""
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM scores")
        self.db.commit()