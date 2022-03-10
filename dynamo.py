#1 Contar los archivos de tablas/
from ast import Num
from cgi import print_form
import os
import time
import pandas
import boto3
import sys

#------------------------------------VARIABLES
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')

######Aqui se cambiará tablasPath por tablas/ previo a la implementación en workflows
tablasPath = "/mnt/c/users/sps/Git-Repos/test-sam-cicd/tablas"
nomTabla = 'test-dynamo-dev'
tablaEstructura = 'sia-gen-adm-estructura-no-catalogos-dev'
#------------------------------------VARIABLES

#2 Listar los archivos
from os import walk
tablasLista = next(walk(tablasPath), (None, None, []))[2]

#3 Cambiar .csv por ambiente -${{env.samEnv}} a cada elemento de la lista.

#### El valor -pre se cambiaría por -${{env.samEnv}} previo a implementación en workflows
tablasListaEnv = [w.replace('.csv', '') for w in tablasLista]
print(tablasListaEnv)
#4 Validar si existen dichas tablas de la lista en AWS
##Se declaran listas de tablas existentes e inexistentes
listaTablasExist = []
listaTablasInexis = []

#-------------------Validación de existencia de tablas y separación en listas.
def validar_tablas(tablas):
    '''Función que nos permite validar la existencia o inexistencia de las tablas'''
    for x in tablas:
        try:
            response = dynamo.describe_table(
            TableName=x)
            listaTablasExist.append(x)
        except:
            # Se separan tablas inexistentes
            listaTablasInexis.append(x)
validar_tablas(tablasListaEnv)
#-----------------------------TABLAS EXISTENTES E INEXISTENTES.
if listaTablasExist != []:
    print('Tablas existentes: ' + ', '.join(listaTablasExist))
if listaTablasInexis != []:
    print('Tablas inexistentes: ' + ', '.join(listaTablasInexis))


def create_table(tablas):
    '''
    Función que crea tablas que no existan.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
    CreateTable is an asynchronous operation. Upon receiving a CreateTable request, 
    DynamoDB immediately returns a response with a TableStatus of CREATING . 
    After the table is created, DynamoDB sets the TableStatus to ACTIVE . 
    You can perform read and write operations only on an ACTIVE table.
    '''
    for x in tablas:
        print("Intentando crear tabla")
        print(x)
        try:
            print("Creando tabla.. " + x)                        
            response = dynamo.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'ID',
                        'AttributeType': 'N'
                    },
                ],
                TableName=x,
                KeySchema=[
                    {
                        'AttributeName': 'ID',
                        'KeyType': 'HASH'
                    },
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {
                        'Key': 'Proyecto',
                        'Value': 'SIA'
                    },
                ]
            )
            response = dynamo.describe_table(TableName=x)
            tableStatus = response['Table']['TableStatus']
            while tableStatus != 'ACTIVE':
                time.sleep(3)
                response = dynamo.describe_table(TableName=x)
                tableStatus = response['Table']['TableStatus']                                           
                print(tableStatus)
            print(f'Tabla {x} creada exitosamente')
        except:
            print("Error al intentar crear tabla.")

#create_table(listaTablasInexis)

def put_item(tablas, tablasPath):
    '''Función que nos permite hacer put_item en DynamoDB basado en los archivos .csv de tablas/'''
    for x in tablas:
        df = pandas.read_csv(tablasPath + '/' + x + '.csv')
        # Con la siguiente forma podemos obtener rows y columns:
        
        print(df.values[2][0])

#-----------------------------Conversión de CSV a diccionario.
df = pandas.read_csv(tablasPath + '/' + nomTabla + '.csv')
#Se eliminan valores nulos a dataframe
first_row_with_all_NaN = df[df.isnull().all(axis=1) == True].index.tolist()[0]
df = df.loc[0:first_row_with_all_NaN-1]
#Se convierte dataframe en diccionario.
data_dict = df.to_dict()

#---------------------------------TABLA DE ESTRUCTURA-----------------------
# Se clona la estructura de la tabla.
tablaEstructura = dynamo.scan(TableName=tablaEstructura)
listaItems = []

diccionarioValidador = {}
def validador_estructura():
    '''Esta función permite crear un diccionario formado por la estructura a seguir de la tabla en cuestión'''
    result = None
    x = 0
    while result is None:
        try:
            # Con esto obtenemos el tipo de dato dependiendo del nombre del campo
            #!!!!CAMBIAR 0 por nombre de tabla a validar!!!!
            campo = tablaEstructura['Items'][0]['ESTRUCTURA']['L'][x]['M']["campo"]['S']
            tipodato = tablaEstructura['Items'][0]['ESTRUCTURA']['L'][x]['M']['tipo']['S']
            diccionarioValidador
            diccionarioValidador.update({campo: tipodato})
            x = x + 1
        except:
            result = 'OK'
            print("Se concluyó captura de validación.")
validador_estructura()

print("\nKEYS de diccionario validador:")
print(f'Total: {len(diccionarioValidador.keys())}')
print(diccionarioValidador)
print("\nKEYS de diccionario de CSV:")
print(f'Total: {len(data_dict.keys())}')
print(data_dict)

#-------------------------------VALIDACIÓN DE NÚMERO DE COLUMNAS. INICIO
if len(data_dict.keys()) > len(diccionarioValidador.keys()):
    print("\nError...")
    print("El número de columnas es MAYOR a la tabla de estructura. Actualizar tabla de estructura antes.")
    sys.exit(0)
elif len(data_dict.keys()) < len(diccionarioValidador.keys()):
    print("\nError...")
    print("El número de columnas es MENOR a la tabla de estructura. Actualizar tabla de estructura antes.")
    sys.exit(0)
#-------------------------------VALIDACIÓN DE NÚMERO DE COLUMNAS. FIN

#-----------------------------Se crean listas que se utilizarán para crear el diccionario. INICIO
# - - - - Lista de valores que se insertarán. INICIO
encabezadosCSV = []
filasCSV = []
profundidad = []
for x, y in data_dict.items():
    encabezadosCSV.append(x) 
    filasCSV.append(y)
    for z in y:
        profundidad.append(z)
# - - - - Lista de valores que se insertarán. FIN

# - - - - Lista diccionario que validará. INICIO
valoresValidadores = []
llavesValidadores = []
for x, y in diccionarioValidador.items():
    llavesValidadores.append(x) 
    valoresValidadores.append(y)
# - - - - Lista diccionario que validará. FIN

#-------------------------------VALIDACIÓN DE NOMBRE COLUMNAS. INICIO
print("Las llaves validadoras son: " + str(llavesValidadores))
print("Los encabezados del CSV son: " + str(encabezadosCSV))

if llavesValidadores != encabezadosCSV:
    print("Las llaves no coinciden")    
    sys.exit(0)

#-------------------------------VALIDACIÓN DE NOMBRE COLUMNAS. INICIO

#-----------------------------Crear diccionario
diccionarioAInsertar = {}
longitudEnc = len(encabezadosCSV)

#Se elimina duplicidad de lista Profundidad.
profundidad = list(dict.fromkeys(profundidad))

longitudProf = len(profundidad)
print(f'Numero de elementos a insertarse: {longitudProf}')

z = 0
while z != longitudProf:
    x = 0
    while x != longitudEnc:
        valor = filasCSV[x][z]
        tipodato = valoresValidadores[x]
        diccionarioAInsertar[encabezadosCSV[x]] = {tipodato: str(valor)}
        ########VALIDACIÓN DE ESTRUCTURA FORMADA
        x = x + 1
        if x == longitudEnc:
            #------------------Inserción de valores en DYNAMO
            response = dynamo.put_item(
            TableName=nomTabla,
            Item=diccionarioAInsertar)
            response
            print("Inserción completada. #" + str(z + 1))
    z = z + 1
#-----------------------------Se termina Crear diccionario
