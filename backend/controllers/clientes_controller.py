from flask import Blueprint
from flask import current_app as app
from Objetos.Cliente import Cliente

import dicttoxml

clientes_bp = Blueprint('clientes_bp', __name__)

@clientes_bp.route('/', methods=['GET'])
def index():
    try:
        clientes = app.config['db_clientes']
        res_clientes = []
        for cliente in clientes:
            cliente: Cliente = cliente
            res_clientes.append({
                "nit": cliente.nit,
                "nombre": cliente.nombre,
                "saldo": cliente.saldo,
                "facturas": cliente.facturas,
                "pagos": cliente.pagos,
            })


        dic_res = {
            "clientes": {
                "cantidadTotal": len(clientes),
                "clientes": res_clientes
            }
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta error", attr_type=False), 500, {'Content-Type': 'application/xml'}
