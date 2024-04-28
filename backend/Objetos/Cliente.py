class Cliente:
    def __init__(self, nit: str, nombre: str, saldo: float = 0):
        self.nit = nit
        self.nombre = nombre
        self.saldo = saldo