from django.shortcuts import render
import requests
import xmltodict
import datetime


def index(request):
    try:
        # crear peticion a la api y enviar los datos a la plantilla
        res = requests.get('http://localhost:5000/api/v1/')
        # obtener el xml
        response = res.content
        # convertir el xml a un diccionario
        data = xmltodict.parse(response)
        # obtener clientes, bancos, dinero_total
        clientes: int = int(data['respuesta']['clientes'])
        bancos: int = int(data['respuesta']['bancos'])
        dinero_total: float = float(data['respuesta']['dinero_total'])
        transactions = data['respuesta']['transacciones']
        # enviar los datos a la plantilla
        return render(request, 'index.html', {'clientes': clientes, 'bancos': bancos, 'dinero_total': dinero_total, 'transactions': transactions})
    except Exception as e:
        return render(request, 'index.html', {'clientes': "NaN", 'bancos': "NaN", 'dinero_total': "NaN", 'transactions': "NaN"})


def clientes(request):
    try:
        res = requests.get('http://localhost:5000/api/v1/clientes')
        # obtener el xml
        response = res.content
        # convertir el xml a un diccionario
        data = xmltodict.parse(response)
        # obtener clientes, bancos, dinero_total
        clientes = data['respuesta']['clientes']['cliente']
        return render(request, 'clientes.html', {'clientes': clientes})
    except Exception as e:
        return render(request, 'clientes.html')


def cliente(request, id):
    try:
        res = requests.get(f'http://localhost:5000/api/v1/clientes/{id}')
        # obtener el xml
        response = res.content
        # convertir el xml a un diccionario
        data = xmltodict.parse(response)
        # obtener cliente
        cliente = data['respuesta']

        # ordenar lista de transacciones por fecha de mas reciente a mas antigua cuando la fecha guardada es un string en formato 'dd/mm/yyyy'
        if cliente['transacciones'] is not None:
            transacciones = cliente['transacciones']['transaccion']
            if not isinstance(transacciones, list):
                cliente['transacciones']['transaccion'] = [transacciones]
            else:
                transacciones.sort(key=lambda x: datetime.datetime.strptime(x['fecha'], '%d/%m/%Y'), reverse=True)

        return render(request, 'views/cliente.html', {'cliente': cliente})
    except Exception as e:
        return render(request, 'views/cliente.html', {'error': str(e)})


def bancos(request):
    try:
        res = requests.get('http://localhost:5000/api/v1/bancos')
        # obtener el xml
        response = res.content
        # convertir el xml a un diccionario
        data = xmltodict.parse(response)
        bancos = data['respuesta']['bancos']['banco']
        return render(request, 'bancos.html', {'bancos': bancos})
    except Exception as e:
        return render(request, 'bancos.html')


def banco(request, id):
    try:
        res = requests.get(f'http://localhost:5000/api/v1/bancos/{id}')
        # obtener el xml
        response = res.content
        # convertir el xml a un diccionario
        data = xmltodict.parse(response)
        # obtener cliente
        banco = data['respuesta']

        # ordenar lista de transacciones por fecha de mas reciente a mas antigua cuando la fecha guardada es un string en formato 'dd/mm/yyyy'
        if banco['transacciones'] is not None:
            transacciones = banco['transacciones']['transaccion']
            if not isinstance(transacciones, list):
                banco['transacciones']['transaccion'] = [transacciones]
            else:
                transacciones.sort(key=lambda x: datetime.datetime.strptime(x['fecha'], '%d/%m/%Y'), reverse=True)


        return render(request, 'views/banco.html', {'banco': banco})
    except Exception as e:
        return render(request, 'views/banco.html', {'error': str(e)})


def consultas(request):
    try:
        return render(request, 'consultas.html')
    except Exception as e:
        return render(request, 'consultas.html')


def ayuda(request):
    try:
        return render(request, 'ayuda.html')
    except Exception as e:
        return render(request, 'ayuda.html')


def datos(request):
    try:
        return render(request, 'views/datos.html')
    except Exception as e:
        return render(request, 'views/datos.html')
