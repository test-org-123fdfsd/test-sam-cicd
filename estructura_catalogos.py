import os
from re import X
import boto3
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')


#validar_tablas(tablasListaEnv)
response = dynamo.list_tables()



#response = dynamo.describe_table(TableName='sia-gen-adm-estructura-catalogos-dev')
listTablas = response['TableNames']

#get_items(listTablas)

#from boto3.dynamodb.conditions import Key, Attr

#dynamodb = boto3.resource('dynamodb')


listaItems = []
def obtener_items():
    result = None
    x = 0
    while result is None:
        try:
            response = dynamo.scan(
            TableName='sia-gen-adm-estructura-catalogos-dev')
            itemTabla = response['Items'][x]['NOMBRE']['S']
            print(itemTabla)
            x = x + 1
            listaItems.append(itemTabla)
        except:
            result = 'OK'
            print("Se terminó de generar la lista de items")
obtener_items()
print(len(listaItems))

