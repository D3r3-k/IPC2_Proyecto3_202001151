class Banco:
    def __init__(self, codigo: str, nombre: str, saldo: float = 0):
        self.codigo = codigo
        self.nombre = nombre
        self.saldo = saldo