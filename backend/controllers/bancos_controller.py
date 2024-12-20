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
                "saldo": banco.saldo
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


@bancos_bp.route('/<id>', methods=['GET'])
def buscar_banco(id):
    try:
        id = int(id)
        banco = buscar_banco(id)
        if banco is None:
            dic_res = {
                "error": "No se encontró el banco con el código " + str(id)
            }
            return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 404, {'Content-Type': 'application/xml'}
        dic_res = {
            "codBanco": banco.codigo,
            "nombre": banco.nombre,
            "saldo": banco.saldo,
            "transacciones": buscar_transacciones_de_banco(banco.codigo)
        }
        dic_xml = dicttoxml.dicttoxml(
            dic_res, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'transaccion')
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
        lista_bancos = obtener_ingresos_por_fecha(fecha)
        dic_xml = dicttoxml.dicttoxml(
            lista_bancos, custom_root="respuesta", attr_type=False, item_func=lambda x: 'ingreso' if x == 'ingresos' else 'bancos')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


@bancos_bp.route('/<codBanco>', methods=['POST'])
def buscar_banco_por_cod(codBanco):
    try:
        data = xmltodict.parse(request.data)
        fecha = data['banco']['fecha']
        print(fecha)
        codBanco = int(codBanco)
        _banco = buscar_banco(codBanco)
        res_banco = None
        if _banco is not None:
            res_banco = {
                "codBanco": _banco.codigo,
                "nombre": _banco.nombre,
                "saldo": _banco.saldo,
                "Ingresos": obtener_ingresos_por_banco(fecha, _banco)
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


def obtener_ingresos_por_banco(fecha: str, banco: Banco):
    ingresos_banco = {
        "banco": banco.codigo,
        "nombre": banco.nombre,
        "ingresos": [],
        "saldo_final": 0
    }
    
    fecha = datetime.strptime(fecha, '%Y-%m')
    meses = []
    for i in range(3):
        mes = fecha.month - i
        año = fecha.year
        if mes <= 0:
            mes += 12
            año -= 1
        meses.append(datetime(año, mes, 1))
    
    for mes in meses:
        mes_str = mes.strftime('%B')

        ingreso_mes = {
            "mes": mes_str,
            "valor": 0
        }

        for transaction in app.config['db_transacciones']:
            if isinstance(transaction, Pago):
                transaction: Pago
                # Convert the date format temporarily
                transaction_fecha = datetime.strptime(
                    transaction.fecha, '%d/%m/%Y')

                if mes <= transaction_fecha <= mes + timedelta(days=31):
                    ingreso_mes["valor"] += transaction.valor

        ingresos_banco["ingresos"].append(ingreso_mes)

    saldo_final = ingresos_banco["saldo_final"]
    for ingreso_mes in ingresos_banco["ingresos"]:
        saldo_final += ingreso_mes["valor"]

    ingresos_banco["saldo_final"] = saldo_final

    return ingresos_banco["ingresos"]


def obtener_ingresos_por_fecha(fecha: str):
    fecha = datetime.strptime(fecha, '%Y-%m')
    meses = []
    for i in range(3):
        mes = fecha.month - i
        año = fecha.year
        if mes <= 0:
            mes += 12
            año -= 1
        meses.append(datetime(año, mes, 1))
    lista_ingresos_por_banco = []
    for banco in app.config['db_bancos']:
        ingresos_banco = {
            "banco": banco.codigo,
            "nombre": banco.nombre,
            "ingresos": [],
            "saldo_final": 0
        }

        for mes in meses:
            mes_str = mes.strftime('%B')

            ingreso_mes = {
                "mes": mes_str,
                "valor": 0
            }

            for transaccion in app.config['db_transacciones']:
                if isinstance(transaccion, Pago):
                    transaccion: Pago
                    # Convert the date format temporarily
                    transaccion_fecha = datetime.strptime(
                        transaccion.fecha, '%d/%m/%Y')

                    if mes <= transaccion_fecha <= mes + timedelta(days=31):
                        ingreso_mes["valor"] += transaccion.valor

            ingresos_banco["ingresos"].append(ingreso_mes)

        saldo_final = ingresos_banco["saldo_final"]
        for ingreso_mes in ingresos_banco["ingresos"]:
            saldo_final += ingreso_mes["valor"]

        ingresos_banco["saldo_final"] = saldo_final

        lista_ingresos_por_banco.append(ingresos_banco)

    return lista_ingresos_por_banco


def buscar_transacciones_de_banco(codBanco: int):
    lista_transacciones = []
    for transaccion in app.config['db_transacciones']:
        if isinstance(transaccion, Pago):
            transaccion: Pago
            if transaccion.codBanco == codBanco:
                lista_transacciones.append({
                    "NITcliente": transaccion.nitCliente,
                    "fecha": transaccion.fecha,
                    "valor": transaccion.valor,
                })
    return lista_transacciones
