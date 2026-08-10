class SingletonMeta(type):
    """Metaclase que garantiza que una clase tenga una unica instancia
    (patron Singleton). Cualquier clase que la use como metaclase va a
    devolver siempre la misma instancia, sin importar cuantas veces se
    llame a su constructor.

    Uso:
        class MiClase(metaclass=SingletonMeta):
            ...
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]