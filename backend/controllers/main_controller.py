from flask import Blueprint
from flask import current_app as app
from Objetos.Banco import Banco

import dicttoxml

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def get():
    clientes = app.config['db_clientes']
    bancos = app.config['db_bancos']
    dinero_total = 0
    for banco in bancos:
        banco: Banco = banco
        dinero_total += banco.saldo

    dic_res = {
        "clientes": len(clientes),
        "bancos": len(bancos),
        "dinero_total": dinero_total
    }
    return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 200, {'Content-Type': 'application/xml'}
