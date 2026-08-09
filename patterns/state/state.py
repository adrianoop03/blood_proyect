class State:
    """Interfaz base para los estados del juego (patrón State).

    Cada estado (menú, jugando, ranking, opciones, etc.) hereda de esta
    clase y sobreescribe los métodos que necesite. El StateManager solo
    conoce esta interfaz, nunca los detalles de cada estado concreto.
    """

    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        """Procesa un evento de pygame (click, teclado, etc.)."""
        pass

    def update(self, dt):
        """Actualiza la lógica del estado. dt = delta time en segundos."""
        pass

    def draw(self, screen):
        """Dibuja el estado en pantalla."""
        pass
