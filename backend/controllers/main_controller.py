from flask import Blueprint, request
from flask import current_app as app
from Objetos.Cliente import Cliente
from Objetos.Banco import Banco
from Objetos.Factura import Factura
from Objetos.Pago import Pago

import re
import dicttoxml
import xmltodict

main_bp = Blueprint('main', __name__)

# PATRONES
patron_nit = r'[0-9]+-[0-9]+'
patron_alfa = r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s-]+'
patron_num = r'[0-9]+'
patron_precio = r'[0-9]+(\.[0-9]{1,2})?'
patron_fecha = r'[0-9]{2}/[0-9]{2}/[0-9]{4}'


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
        "dinero_total": dinero_total,
        "transacciones": len(app.config['db_transacciones'])
    }
    return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 200, {'Content-Type': 'application/xml'}


@main_bp.route('/', methods=['POST'])
def post():
    try:
        db_clientes = app.config['db_clientes']
        db_bancos = app.config['db_bancos']
        data = request.data
        data = xmltodict.parse(data)
        clientes = data['config']['clientes']['cliente']
        bancos = data['config']['bancos']['banco']

        clientes_creados = 0
        clientes_actualizados = 0
        bancos_creados = 0
        bancos_actualizados = 0
        lista_errores = []

        for cliente in clientes:
            nit = cliente['NIT']
            nombre = cliente['nombre']
            nit = re.fullmatch(patron_nit, nit)
            nombre = re.fullmatch(patron_alfa, nombre)
            if nit is None or nombre is None:
                lista_mensajes = []
                obj_error = {
                    "tipo": "cliente"
                }
                if nit is None:
                    obj_error['NIT'] = cliente['NIT']
                    lista_mensajes.append("NIT no valido")
                if nombre is None:
                    obj_error['NIT'] = cliente['NIT']
                    lista_mensajes.append("Nombre no valido")
                obj_error['mensaje'] = lista_mensajes
                lista_errores.append(obj_error)
                continue
            nit = nit.group()
            nombre = nombre.group()
            existe = buscar_cliente(nit)
            if existe is None:
                nuevo_cliente = Cliente(nit, nombre)
                db_clientes.append(nuevo_cliente)
                clientes_creados += 1
            else:
                existe.nombre = nombre
                clientes_actualizados += 1

        for banco in bancos:
            codigo = banco['codigo']
            nombre = banco['nombre']
            codigo = re.fullmatch(patron_num, codigo)
            nombre = re.fullmatch(patron_alfa, nombre)
            if codigo is None or nombre is None:
                lista_mensajes = []
                obj_error = {
                    "tipo": "banco"
                }
                if codigo is None:
                    obj_error['codigo'] = banco['codigo']
                    lista_mensajes.append("Codigo no valido")
                if nombre is None:
                    obj_error['codigo'] = banco['codigo']
                    lista_mensajes.append("Nombre no valido")
                obj_error['mensaje'] = lista_mensajes
                lista_errores.append(obj_error)
                continue
            codigo = int(codigo.group())
            nombre = nombre.group()
            existe = buscar_banco(codigo)
            if existe is None:
                nuevo_banco = Banco(codigo, nombre)
                db_bancos.append(nuevo_banco)
                bancos_creados += 1
            else:
                existe.nombre = nombre
                bancos_actualizados += 1

        dic_res = {
            "clientes": {
                "creados": clientes_creados,
                "actualizados": clientes_actualizados
            },
            "bancos": {
                "creados": bancos_creados,
                "actualizados": bancos_actualizados
            },
            "errores": lista_errores if len(lista_errores) > 0 else {
                "mensaje": "No se encontraron errores"
            },
            "mensaje": "Se crearon los clientes y bancos"
        }
        dic_xml = dicttoxml.dicttoxml(
            dic_res, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'error')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        print(e)
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


@main_bp.route('/', methods=['PUT'])
def put():
    try:
        db_transacciones = app.config['db_transacciones']

        data = request.data
        data = xmltodict.parse(data)
        facturas = data['transacciones']['facturas']['factura']
        pagos = data['transacciones']['pagos']['pago']

        nuevas_facturas = 0
        facturas_duplicadas = 0
        facturas_con_error = 0

        nuevos_pagos = 0
        pagos_duplicados = 0
        pagos_con_error = 0

        lista_errores = []

        for factura in facturas:
            numeroFactura = factura['numeroFactura']
            nitCliente = factura['NITcliente']
            fecha = factura['fecha']
            valor = factura['valor']

            numeroFactura = re.fullmatch(patron_alfa, numeroFactura)
            nitCliente = re.fullmatch(patron_nit, nitCliente)
            fecha = re.findall(patron_fecha, fecha)
            valor = re.fullmatch(patron_precio, valor)

            if numeroFactura is None or nitCliente is None or fecha is None or valor is None:
                lista_mensajes = []
                obj_error = {
                    "tipo": "factura"
                }
                if numeroFactura is None:
                    obj_error['numeroFactura'] = factura['numeroFactura']
                    lista_mensajes.append("Numero de factura no valido")
                if nitCliente is None:
                    obj_error['NITcliente'] = factura['NITcliente']
                    lista_mensajes.append("NIT no valido")
                if fecha is None:
                    obj_error['fecha'] = factura['fecha']
                    lista_mensajes.append("Fecha no valida")
                if valor is None:
                    obj_error['valor'] = factura['valor']
                    lista_mensajes.append("Valor no valido")
                obj_error['mensaje'] = lista_mensajes
                lista_errores.append(obj_error)
                facturas_con_error += 1
                continue

            numeroFactura = numeroFactura.group()
            nitCliente = nitCliente.group()
            fecha = fecha[0]
            valor = float(valor.group())

            _cliente = buscar_cliente(nitCliente)
            if _cliente is None:
                lista_errores.append(
                    {
                        "tipo": "factura",
                        "NITcliente": nitCliente,
                        "mensaje": "Cliente no encontrado"
                    }
                )
                facturas_con_error += 1
                continue

            _factura = buscar_transacciones(numeroFactura)
            if _factura is None:
                _cliente.saldo -= valor
                nueva_factura = Factura(
                    numeroFactura, _cliente.nit, fecha, valor)
                db_transacciones.append(nueva_factura)
                nuevas_facturas += 1
            else:
                facturas_duplicadas += 1

        for pago in pagos:
            codigoBanco = pago['codigoBanco']
            fecha = pago['fecha']
            nitCliente = pago['NITcliente']
            valor = pago['valor']

            codigoBanco = re.fullmatch(patron_num, codigoBanco)
            fecha = re.findall(patron_fecha, fecha)
            nitCliente = re.fullmatch(patron_nit, nitCliente)
            valor = re.fullmatch(patron_precio, valor)

            if codigoBanco is None or fecha is None or nitCliente is None or valor is None:
                lista_mensajes = []
                obj_error = {
                    "tipo": "pago"
                }
                if codigoBanco is None:
                    obj_error['codigoBanco'] = pago['codigoBanco']
                    lista_mensajes.append("Codigo de banco no valido")
                if fecha is None:
                    obj_error['fecha'] = pago['fecha']
                    lista_mensajes.append("Fecha no valida")
                if nitCliente is None:
                    obj_error['NITcliente'] = pago['NITcliente']
                    lista_mensajes.append("NIT no valido")
                if valor is None:
                    obj_error['valor'] = pago['valor']
                    lista_mensajes.append("Valor no valido")
                obj_error['mensaje'] = lista_mensajes
                lista_errores.append(obj_error)
                pagos_con_error += 1
                continue

            codigoBanco = int(codigoBanco.group())
            fecha = fecha[0]
            nitCliente = nitCliente.group()
            valor = float(valor.group())

            _banco = buscar_banco(codigoBanco)
            if _banco is None:
                lista_errores.append(
                    {
                        "tipo": "pago",
                        "codigoBanco": codigoBanco,
                        "mensaje": "Banco no encontrado"
                    }
                )
                pagos_con_error += 1
                continue

            _cliente = buscar_cliente(nitCliente)
            if _cliente is None:
                lista_errores.append(
                    {
                        "tipo": "pago",
                        "NITcliente": nitCliente,
                        "mensaje": "Cliente no encontrado"
                    }
                )
                pagos_con_error += 1
                continue

            nuevo_pago = Pago(_banco.codigo, fecha, _cliente.nit, valor)
            if nuevo_pago in db_transacciones:
                pagos_duplicados += 1
                db_transacciones.append(nuevo_pago)
            else:
                _banco.saldo += valor
                _cliente.saldo += valor
                db_transacciones.append(nuevo_pago)
                nuevos_pagos += 1

        dic_res = {
            "facturas": {
                "nuevasFacturas": nuevas_facturas,
                "facturasDuplicadas": facturas_duplicadas,
                "facturasConError": facturas_con_error
            },
            "pagos": {
                "nuevosPagos": nuevos_pagos,
                "pagosDuplicados": pagos_duplicados,
                "pagosConError": pagos_con_error
            },
            "errores": lista_errores if len(lista_errores) > 0 else {
                "mensaje": "No se encontraron errores"
            },
        }

        dic_xml = dicttoxml.dicttoxml(
            dic_res, custom_root="respuesta", attr_type=False)
        dic_xml = dic_xml.replace(b'item', b'error')
        return dic_xml, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


@main_bp.route('/', methods=['DELETE'])
def delete():
    try:
        app.config['db_clientes'] = []
        app.config['db_bancos'] = []
        dic_res = {
            "mensaje": "Se eliminaron todos los clientes y bancos"
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        dic_res = {
            "error": str(e)
        }
        return dicttoxml.dicttoxml(dic_res, custom_root="respuesta", attr_type=False), 500, {'Content-Type': 'application/xml'}


def buscar_cliente(nit: str):
    for cliente in app.config['db_clientes']:
        cliente: Cliente
        if cliente.nit == nit:
            return cliente
    return None


def buscar_banco(codigo: int):
    for banco in app.config['db_bancos']:
        banco: Banco
        if banco.codigo == codigo:
            return banco
    return None


def buscar_transacciones(nit: str, ):
    for transaccion in app.config['db_transacciones']:
        if isinstance(transaccion, Factura):
            transaccion: Factura = transaccion
            if transaccion.nitCliente == nit:
                return transaccion
        elif isinstance(transaccion, Pago):
            transaccion: Pago = transaccion
            if transaccion.nitCliente == nit:
                return transaccion
    return None
