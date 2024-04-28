from flask import Blueprint, request
from flask import current_app as app
from Objetos.Banco import Banco
from Objetos.Pago import Pago


from datetime import datetime
from datetime import timedelta
import dicttoxml
import xmltodict

bancos_bp = Blueprint('bancos_bp', __name__)


@bancos_bp.route('/', methods=['GET'])
def index():
    try:
        bancos = app.config['db_bancos']
        res_bancos = []
        for banco in bancos:
            banco: Banco = banco
            res_bancos.append({
                "codBanco": banco.codigo,
                "nombre": banco.nombre,
                "saldo": banco.saldo,
                "transacciones": banco.transacciones
            })

        dic_res = {
            "cantidadTotal": len(bancos),
            "bancos": res_bancos
        }
        dic_xml = dicttoxml.dicttoxml(
            dic_res, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'banco')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


@bancos_bp.route('/', methods=['POST'])
def buscar_banco_fecha():
    try:
        data = xmltodict.parse(request.data)
        fecha = data['banco']['fecha']
        codBanco = data['banco']['codBanco']
        codBanco = int(codBanco)
        _banco = buscar_banco(codBanco)
        res_banco = None
        if _banco is not None:
            res_banco = {
                "codBanco": _banco.codigo,
                "nombre": _banco.nombre,
                "saldo": _banco.saldo,
                "Ingresos": obtener_ingresos_fecha(fecha, _banco)
            }

        if res_banco is None:
            dic_res = {
                "error": "No se encontró el banco con el código " + str(codBanco)
            }
            return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 404, {'Content-Type': 'application/xml'}

        dic_xml = dicttoxml.dicttoxml(
            res_banco, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'ingreso')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


@bancos_bp.route('/<codBanco>', methods=['GET'])
def buscar_banco(codBanco):
    try:
        codBanco = int(codBanco)
        _banco = buscar_banco(codBanco)
        res_banco = None
        if _banco is not None:
            res_banco = {
                "codBanco": _banco.codigo,
                "nombre": _banco.nombre,
                "saldo": _banco.saldo,
                "Ingresos": obtener_ingresos(_banco)
            }

        if res_banco is None:
            dic_res = {
                "error": "No se encontró el banco con el código " + str(codBanco)
            }
            return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 404, {'Content-Type': 'application/xml'}

        dic_xml = dicttoxml.dicttoxml(
            res_banco, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'ingreso')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


def buscar_banco(codigo: int):
    for banco in app.config['db_bancos']:
        banco: Banco
        if banco.codigo == codigo:
            return banco
    return None


def obtener_ingresos(banco: Banco):
    # obtener los ingresos de un banco de los 3 meses anteriores a la fecha
    lista_ingresos = []
    for transaccion in app.config['db_transacciones']:
        if isinstance(transaccion, Pago):
            transaccion: Pago
            if transaccion.codBanco == banco.codigo:
                lista_ingresos.append({
                    "fecha": transaccion.fecha,
                    "valor": transaccion.valor
                })
    return lista_ingresos

def obtener_ingresos_fecha(fecha: str, banco: Banco):
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    meses = []
    for i in range(3):
        mes = fecha.month - i
        año = fecha.year
        if mes <= 0:
            mes += 12
            año -= 1
        meses.append(datetime(año, mes, 1))

    lista_ingresos = []

    for mes in meses:
        mes_str = mes.strftime('%B')
        ingreso_mes = {
            "mes": mes_str,
            "fechas": [],
            "valor": 0
        }

        for transaccion in app.config['db_transacciones']:
            if isinstance(transaccion, Pago):
                transaccion: Pago
                transaccion_fecha = datetime.strptime(transaccion.fecha, '%d/%m/%Y')
                if transaccion.codBanco == banco.codigo and mes <= transaccion_fecha <= mes + timedelta(days=31):
                    ingreso_mes["fecha"].append(transaccion.fecha)
                    ingreso_mes["valor"] += transaccion.valor
        lista_ingresos.append(ingreso_mes)

    return lista_ingresos

