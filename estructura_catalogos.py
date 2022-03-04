import os
import boto3
import time
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')


#validar_tablas(tablasListaEnv)
response = dynamo.list_tables()
listTablas = response['TableNames']


#response = dynamo.describe_table(TableName='sia-gen-adm-estructura-catalogos-dev')

#get_items(listTablas)
listaTablasExist = []
listaTablasInexis = []

def get_items(tablas):
    for x in tablas:
        #time.sleep(3)
        try:
            
            response = dynamo.batch_get_item(
                RequestItems={
                    'sia-gen-adm-estructura-catalogos-dev': {
                        'Keys': [
                            {
                                'NOMBRE': {
                                    'S': 'sia-afore-cat-tipo-valor-dev'
                                }
                            },
                        ]
                        }
                    }
            )
            #print(response)
            print(x)
            print(response['Responses']['sia-gen-adm-estructura-catalogos-dev'][0]['NOMBRE']['S'])
            #time.sleep(3)
            listaTablasExist.append(x)
        except Exception as e:
            print(e)
            listaTablasInexis.append(x)
            #print(f'{x} no está en la lista')

#if listaTablasExist != []:


get_items(listTablas)
print('Tablas existentes: ' + ', '.join(listaTablasExist))

#if listaTablasInexis != []:
print('Tablas inexistentes: ' + ', '.join(listaTablasInexis))
print(len(listaTablasInexis))