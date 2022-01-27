# from asyncio.unix_events import BaseChildWatcher
# from lib2to3.pgen2 import driver
import argparse
from cmath import log
from math import prod
import os
import sys
from xml import dom

import boto3
import time
import argparse
global args


client = boto3.client('route53')

# Failover Principal

# Se obtienen las variables parseadas
parser = argparse.ArgumentParser()

# Hosted zone
parser.add_argument(
    "-hz",
    "--hosted-zone-id",
    required=True,
    action="store",
    dest="hosted_zone_id",
    help="Hosted zone ID.",
    default=None,
)
# Dominio Principal de produccion
parser.add_argument(
    "-prd",
    "--production-domain",
    required=True,
    action="store",
    dest="production_domain",
    help="Production domain.",
    default=None,
)

# Cachamos los valores parseados
args = parser.parse_args()

production_domain = args.production_domain
hosted_zone_id = args.hosted_zone_id

# Se listan los records actuales de la hosted zone.

response = client.list_resource_record_sets(
    HostedZoneId=hosted_zone_id
)

# Aquí generamos la lista desde Route 53:
listaR53 = response["ResourceRecordSets"]

# Con esto obtenemos el valor del nombre dependiendo del ID de la lista.
# response["ResourceRecordSets"][0]["Name"]


#thislist = {'ResponseMetadata': {'RequestId': '5d8b6033-9bd8-485e-8e0a-023926e2a9b9', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '5d8b6033-9bd8-485e-8e0a-023926e2a9b9', 'content-type': 'text/xml', 'content-length': '2526', 'date': 'Wed, 26 Jan 2022 17:23:11 GMT'}, 'RetryAttempts': 0}, 'ResourceRecordSets': [{'Name': 'charlycloudy.com.', 'Type': 'A', 'AliasTarget': {'HostedZoneId': 'Z1UJRXOUMOOFQ8', 'DNSName': 'd-3dxauuvmwb.execute-api.us-east-1.amazonaws.com.', 'EvaluateTargetHealth': True}}, {'Name': 'charlycloudy.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': [{'Value': 'ns-1787.awsdns-31.co.uk.'}, {'Value': 'ns-442.awsdns-55.com.'}, {'Value': 'ns-1186.awsdns-20.org.'}, {'Value': 'ns-714.awsdns-25.net.'}]}, {'Name': 'charlycloudy.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': [{'Value': 'ns-1787.awsdns-31.co.uk. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400'}]}, {'Name': 'drtarget1.charlycloudy.com.', 'Type': 'CNAME', 'TTL': 300, 'ResourceRecords': [{'Value': 'google.com'}]}, {'Name': 'drtarget2.charlycloudy.com.', 'Type': 'CNAME', 'TTL': 300, 'ResourceRecords': [{'Value': 'stackoverflow.com'}]}, {'Name': 'produccion.charlycloudy.com.', 'Type': 'CNAME', 'SetIdentifier': 'DR region', 'Failover': 'SECONDARY', 'TTL': 60, 'ResourceRecords': [{'Value': 'drtarget1.charlycloudy.com'}], 'HealthCheckId': 'a04de13d-00ea-408a-b0bf-f98aa7d3e948'}, {'Name': 'produccion.charlycloudy.com.', 'Type': 'CNAME', 'SetIdentifier': 'Production region', 'Failover': 'PRIMARY', 'TTL': 60, 'ResourceRecords': [{'Value': 'drtarget2.charlycloudy.com'}], 'HealthCheckId': 'a04de13d-00ea-408a-b0bf-f98aa7d3e948'}, {'Name': 'sps.charlycloudy.com.', 'Type': 'CNAME', 'TTL': 300, 'ResourceRecords': [{'Value': 'spsolutions.com.mx'}]}], 'IsTruncated': False, 'MaxItems': '100'}

# RR = print(thislist["ResourceRecordSets"][5])
# Contamos la lista de Route 53.
longRRS = len(listaR53)
print("En total hay " + str(longRRS) + " registros en Route53 (AWS): \n")
dominio = "produccion.charlycloudy.com."
print("Dominio de producción: " + dominio)
print("#--------------------------------------------------")
#1 Función para obtener los ResourceRecordSets que contengan como valor produccion.charlycloudy.com


def obtenerDominios(listaRRS, lengthRRS, dom):
    y = 1
    primario = ""
    secundario = ""
    for x in range(lengthRRS):
        # Se obtiene el nombre de los registros
        RRSFP = listaRRS[x]["Name"]
        if RRSFP == dom:
            # Contador de mismo dominio
            y= y + 1
            
            # Prioridad de failover.
            failover = listaRRS[x]["Failover"]
            
            #Tipo de record.
            type = listaRRS[x]["Type"]

            # Objetivos del failover
            target = listaRRS[x]["ResourceRecords"]
            target = target[0]
            target = target["Value"]

            
            if failover == "PRIMARY" or "SECONDARY":
                print("Prioridad de failover: " + failover) 
                print("Objetivo de failover: " + target)
                print("Tipo de record: " + type)
                print("#--------------------------------------------------")
                if failover == "PRIMARY":
                    primario = target
                elif failover == "SECONDARY":
                    secundario = target
    return primario, secundario
    # print("#" + str(x + 1) + ": " + str(RRSFP))
    # print("El dominio " + dom + " aparece: " + str(y - 1) + " veces")
# obtenerDominios(listaR53, longRRS, dominio)


def obtenerFailover():     
    failovers = obtenerDominios(listaR53, longRRS, dominio)
    print(failovers[0])

obtenerFailover()
'''
# Conversión de valores de los dominios. Aquí se invierten entre ellos sus valores actuales.
temp_primary_domain = primary_domain
temp_failover_domain = failover_domain

new_primary_domain = temp_failover_domain
new_failover_domain = temp_primary_domain

print(f"Nuevo primario {new_primary_domain}")
print(f"Nuevo failover {new_failover_domain}")
'''


# Se comenta Switch hasta obtener los targets PRIMARY y SECONDARY correctamente.
'''
records = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Failover': 'PRIMARY',
                    # Se creo healtcheck para este subdominio
                    'HealthCheckId': 'a04de13d-00ea-408a-b0bf-f98aa7d3e948',
                    'Name': production_domain,
                    'ResourceRecords': [
                        {
                            'Value': new_primary_domain,
                        },
                    ],
                    'SetIdentifier': 'Production region',
                    'TTL': 60,
                    'Type': 'CNAME',
                },
            },
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Failover': 'SECONDARY',
                    # Se usa mismo healtcheck ID para prueba
                    'HealthCheckId': 'a04de13d-00ea-408a-b0bf-f98aa7d3e948',
                    'Name': production_domain,
                    'ResourceRecords': [
                        {
                            'Value': new_failover_domain,
                        },
                    ],
                    'SetIdentifier': 'DR region',
                    'TTL': 60,
                    'Type': 'CNAME',
                },
            },
        ],
        'Comment': 'Failover Produccion a DR',
    }

print(records)


response = client.change_resource_record_sets(
    ChangeBatch=records,
    HostedZoneId=hosted_zone_id,
)

print(response)
'''
