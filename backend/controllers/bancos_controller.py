from flask import Blueprint
from flask import current_app as app
from Objetos.Banco import Banco

import dicttoxml

bancos_bp = Blueprint('bancos_bp', __name__)

@bancos_bp.route('/', methods=['GET'])
def index():
    try:
        bancos = app.config['db_bancos']
        res_bancos = []
        for banco in bancos:
            banco: Banco = banco
            res_bancos.append({
                "codBanco": banco.codBanco,
                "nombre": banco.nombre,
                "saldo": banco.saldo,
                "transacciones": banco.transacciones
            })


        dic_res = {
            "bancos": {
                "cantidadTotal": len(bancos),
                "bancos": res_bancos
            }
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta error", attr_type=False), 500, {'Content-Type': 'application/xml'}
