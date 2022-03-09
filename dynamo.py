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

path, dirs, files = next(os.walk(tablasPath))
file_count = len(files)
#print(file_count)

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


############5 ¿Existen todas las tablas?
def validar_tablas(tablas):
    '''Función que nos permite validar la existencia o inexistencia de las tablas'''
    for x in tablas:
        try:
            response = dynamo.describe_table(
            TableName=x)
            listaTablasExist.append(x)
        except:
            ###########7.0 Si NO, Se separará la lista en 2. Tablas inexistentes y Tablas existentes
            listaTablasInexis.append(x)
        
validar_tablas(tablasListaEnv)

###########6.0 Si SÍ,  Imprimir Tablas por actualizar: <tablas-existentes>
if listaTablasExist != []:
    print('Tablas existentes: ' + ', '.join(listaTablasExist))
#7.1 Imprimir Tablas por actualizar: <tablas-existentes> y Tablas por crear: <tablas-no-existentes>
if listaTablasInexis != []:
    print('Tablas inexistentes: ' + ', '.join(listaTablasInexis))

#8.0 Se intentará hacer un CREATE de la tabla    
def create_table(tablas):
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
    #CreateTable is an asynchronous operation. Upon receiving a CreateTable request, 
    #DynamoDB immediately returns a response with a TableStatus of CREATING . 
    #After the table is created, DynamoDB sets the TableStatus to ACTIVE . 
    #You can perform read and write operations only on an ACTIVE table.
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

#-----------------------------Conversión de CSV a diccionario
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

#-------------------------------VALIDACIÓN DE COLUMNAS
if len(data_dict.keys()) > len(diccionarioValidador.keys()):
    print("\nError...")
    print("El número de columnas es MAYOR a la tabla de estructura. Actualizar tabla de estructura antes.")
    sys.exit(0)
elif len(data_dict.keys()) < len(diccionarioValidador.keys()):
    print("El número de columnas es MENOR a la tabla de estructura. Actualizar tabla de estructura antes.")
    sys.exit(0)

#-----------------------------CSV convertido a diccionario que se validará con tabla
encabezadosCSV = []
filasCSV = []
profundidad = []
#-----------------------------Se crean listas que se utilizarán para crear el diccionario.
for x, y in data_dict.items():
    encabezadosCSV.append(x) 
    filasCSV.append(y)
    for z in y:
        profundidad.append(z)
#-----------------------------Crear diccionario
diccionarioAInsertar = {}
longitudEnc = len(encabezadosCSV)

#Se elimina duplicidad de lista Profundidad
profundidad = list(dict.fromkeys(profundidad))

longitudProf = len(profundidad)
print(f'Longitud de profundidad: {longitudProf}')
z = 0

############################TEMPORAL
tipodato = 'N'
while z != longitudProf:
    x = 0
    while x != longitudEnc:
        valor = filasCSV[x][z]
        if x == 0:
            # Esto es necesario cambiarlo por el tipo de dato de estructura para el PK
            tipodato = 'N'
        diccionarioAInsertar[encabezadosCSV[x]] = {tipodato: str(valor)}
        tipodato = 'S'
        ########VALIDACIÓN DE ESTRUCTURA FORMADA
        
        x = x + 1
        if x == longitudEnc:
            # Inserción
            response = dynamo.put_item(
            TableName=nomTabla,
            Item=diccionarioAInsertar)
            response
            print("Inserción completada.")
    z = z + 1

#-----------------------------Se termina Crear diccionario
