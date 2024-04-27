class Banco:
    def __init__(self, codBanco: str, nombre: str, saldo: float = 0, transacciones: list = []):
        self.codBanco = codBanco
        self.nombre = nombre
        self.saldo = saldo
        self.transacciones = transacciones