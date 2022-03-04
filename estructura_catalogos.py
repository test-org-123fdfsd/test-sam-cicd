import os
import boto3
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')


#validar_tablas(tablasListaEnv)
response = dynamo.list_tables()
listTablas = response['TableNames']


#response = dynamo.describe_table(TableName='sia-gen-adm-estructura-catalogos-dev')


def get_items(tablas):
    for x in tablas:
        try:
            response = dynamo.get_item(
            TableName='sia-gen-adm-estructura-catalogos-dev',
            Key={
                'NOMBRE': {
                    'S': x
                }
            }
            )
            if response != 0:
                print(f'{x} no está en la tabla de Estructura de Catálogos')
        except:
            print(f'{x} no está en la tabla de Estructura de Catálogos')


get_items(listTablas)
