from django.shortcuts import render
import requests
import xmltodict


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
        # enviar los datos a la plantilla
        return render(request, 'index.html', {'clientes': clientes, 'bancos': bancos, 'dinero_total': dinero_total})
    except Exception as e:
        return render(request, 'index.html', {'clientes': "NaN", 'bancos': "NaN", 'dinero_total': "NaN"})

def clientes(request):
    try:
        return render(request, 'clientes.html')
    except Exception as e:
        return render(request, 'clientes.html')
    

def cliente(request, id):
    try:
        return render(request, 'views/cliente.html')
    except Exception as e:
        return render(request, 'views/cliente.html')
    

def bancos(request):
    try:
        return render(request, 'bancos.html')
    except Exception as e:
        return render(request, 'bancos.html')
    

def banco(request, id):
    try:
        return render(request, 'views/banco.html')
    except Exception as e:
        return render(request, 'views/banco.html')
    
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