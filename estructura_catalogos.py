from ast import NotIn
import os
from re import X
from unittest import result
import boto3
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')


#Se genera lista de tablas
response = dynamo.list_tables()

#response = dynamo.describe_table(TableName='sia-gen-adm-estructura-catalogos-dev')
listTablasSIA = response['TableNames']
#Se le quita el ambiente a las tablas que la tengan para validar items
listaTablasItems = [w.replace('-dev', '') for w in listTablasSIA]

##### Se genera lista de items de tabla de 
listaItems = []
def obtener_items():
    result = None
    x = 0
    while result is None:
        try:
            response = dynamo.scan(
            TableName='sia-gen-adm-estructura-catalogos-dev')
            itemTabla = response['Items'][x]['NOMBRE']['S']
            x = x + 1
            listaItems.append(itemTabla)
        except:
            result = 'OK'
            print("Se terminó de generar la lista de items")
obtener_items()

print(f'Total de items en lista: {len(listaItems)}')

tablasNoEstructura = []
def validador_items():
    x = 0
    result = None
    while result is None:
        try:
            if listaTablasItems[x] not in listaItems:
                tablasNoEstructura.append(listaTablasItems[x])
                print(f'{listaTablasItems[x]} no está en la tabla de Estructura Catalogos')
            x = x + 1
        except:
            result = 'OK'
            print("Proceso terminado")    
validador_items()
print("Lista de tablas NO ESTÁN EN ESCRUCTURA:")
print(tablasNoEstructura)
print(f'Total de tablas que no están en Estructura Catálogos: {len(tablasNoEstructura)}')
