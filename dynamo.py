#1 Contar los archivos de tablas/
import os
import time
######Aqui se cambiará tablasPath por tablas/ previo a la implementación en workflows
tablasPath = "/mnt/c/users/sps/Git-Repos/test-sam-cicd/tablas"
path, dirs, files = next(os.walk(tablasPath))
file_count = len(files)
print(file_count)

#2 Listar los archivos
from os import walk

tablasLista = next(walk(tablasPath), (None, None, []))[2]
#Lista de tablas en formato .csv
print(tablasLista)

#3 Cambiar .csv por ambiente -${{env.samEnv}} a cada elemento de la lista.

#### El valor -pre se cambiaría por -${{env.samEnv}} previo a implementación en workflows
tablasListaEnv = [w.replace('.csv', '-dev') for w in tablasLista]
print(tablasListaEnv)
#4 Validar si existen dichas tablas de la lista en AWS
##Se declaran listas de tablas existentes e inexistentes
listaTablasExist = []
listaTablasInexis = []

import boto3
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')

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
print('Tablas existentes:' + str(listaTablasExist))
#7.1 Imprimir Tablas por actualizar: <tablas-existentes> y Tablas por crear: <tablas-no-existentes>
if listaTablasInexis != []:
    print('Tablas inexistentes:' + str(listaTablasInexis))

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

create_table(listaTablasInexis)


print("Experimentación PANDAS")
import pandas
df = pandas.read_csv(tablasPath + '/test-dynamo.csv')
#print(df)
#print(df.loc[1,:])
#print(df.loc[[0]])

# Con la siguiente forma podemos obtener rows y columns:
print(df.values[1][0])




#def update_table():
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.update_table

#def put_item():
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.update_item

#def update_item():
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.update_item

###########6.1 Se usará la misma lista
###########6.2 Se entrará al contenido del csv de cada elemento de la lista
###########6.3 Se intentará hacer UPDATE a tabla
####7.2 ¿Qué lista es?
####Si es lista de tablas EXISTENTES
#7.3 SI es existente seguir pasos 6.1-6.3

####Si es lista de tablas INEXISTENTES
#8.0 Se entrará al contenido del csv de cada elemento de la lista
#8.1 Se intentará hacer un CREATE de la tabla    
#8.2 Se intentará hacer un INSERT/UPDATE a la tabla


#Creamos una función que sea CREATE_TABLE y dentro le ponemos un for en la lista de tablas EXISTENTES.

#Y otra función que sea UPDATE_TABLE y dentro el for en la lista de tablas EXISTENTES
