class Pago:
    def __init__(self, codBanco: int, fecha: str, nitCliente: int, valor: float):
        self.codBanco = codBanco
        self.fecha = fecha
        self.nitCliente = nitCliente
        self.valor = valor