from flask import Blueprint
from flask import current_app as app
from Objetos.Cliente import Cliente
from Objetos.Factura import Factura
from Objetos.Pago import Pago

import dicttoxml

clientes_bp = Blueprint('clientes_bp', __name__)


@clientes_bp.route('/', methods=['GET'])
def index():
    try:
        clientes = app.config['db_clientes']
        # crear un diccionario con los datos del cliente donde el item sea "cliente" y el valor sea el cliente
        res_clientes = []
        for cliente in clientes:
            cliente: Cliente = cliente
            res_cliente = {
                "nit": cliente.nit,
                "nombre": cliente.nombre,
                "saldo": cliente.saldo,
                "facturas": cliente.facturas,
                "pagos": cliente.pagos,
            }
            res_clientes.append(res_cliente)

        dic_res = {
            "cantidadTotal": len(clientes),
            "clientes": res_clientes
        }
        dic_xml = dicttoxml.dicttoxml(
            dic_res, custom_root="respuesta", attr_type=False)
        # remplazar la etiqueta "item" por "cliente"
        dic_xml = dic_xml.replace(b'item', b'cliente')
        # retornar el diccionario convertido a xml
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


@clientes_bp.route('/<nit>', methods=['GET'])
def buscar_cliente(nit):
    try:
        nit = nit
        clientes = app.config['db_clientes']
        res_cliente = None
        for cliente in clientes:
            cliente: Cliente = cliente
            if cliente.nit == nit:
                res_cliente = {
                    "nit": cliente.nit,
                    "nombre": cliente.nombre,
                    "saldo": cliente.saldo,
                    "transacciones": buscar_transacciones(nit)
                }
                break

        if res_cliente is None:
            dic_res = {
                "error": "No se encontró el cliente con el NIT " + str(nit)
            }
            return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 404, {'Content-Type': 'application/xml'}
        dic_xml = dicttoxml.dicttoxml(
            res_cliente, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'transaccion')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}

def buscar_transacciones(nit: str):
    lista_transacciones = []
    for transaccion in app.config['db_transacciones']:
        if isinstance(transaccion, Factura):
            transaccion: Factura = transaccion
            if transaccion.nitCliente == nit:
                lista_transacciones.append({
                    "tipo": "Factura",
                    "numFactura": transaccion.numFactura,
                    "fecha": transaccion.fecha,
                    "valor": transaccion.valor
                })
        elif isinstance(transaccion, Pago):
            transaccion: Pago = transaccion
            if transaccion.nitCliente == nit:
                lista_transacciones.append({
                    "tipo": "Pago",
                    "codigoBanco": transaccion.codBanco,
                    "fecha": transaccion.fecha,
                    "valor": transaccion.valor
                })
    return lista_transacciones