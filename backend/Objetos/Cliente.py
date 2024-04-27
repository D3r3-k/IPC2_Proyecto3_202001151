class Cliente:
    def __init__(self, nit: int, nombre: str, saldo: float = 0, facturas: list = [], pagos: list = []):
        self.nit = nit
        self.nombre = nombre
        self.saldo = saldo
        self.facturas = facturas
        self.pagos = pagos