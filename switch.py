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


#1 Función para obtener los ResourceRecordSets que contengan como valor produccion.charlycloudy.com
def obtenerDominios():
    print("#--------------------------------------------------")
    # Se listan los records actuales de la hosted zone.
    response = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id
    )

    # Aquí generamos la lista desde Route 53:
    listaRRS = response["ResourceRecordSets"]

    # Contamos la lista de Route 53.
    lengthRRS = len(listaRRS)
    print("En total hay " + str(lengthRRS) + " registros en Route53 (AWS): \n")
    dom = "produccion.charlycloudy.com."
    print("Dominio de producción: " + dom)
    print("#--------------------------------------------------")
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
    failovers = obtenerDominios()
    print("Valor actual de primario: " + failovers[0])
    print("Valor actual de secundario: " + failovers[1])

    primary_domain = failovers[0]
    failover_domain = failovers[1]

    temp_primary_domain = primary_domain
    temp_failover_domain = failover_domain

    new_primary_domain = temp_failover_domain
    new_failover_domain = temp_primary_domain

    print(f"Nuevo primario {new_primary_domain}")
    print(f"Nuevo failover {new_failover_domain}")
    return new_primary_domain, new_failover_domain


# Switch para cambiar failovers.
def switch():
    failoversNuevos = obtenerFailover()
    new_primary_domain_switch = failoversNuevos[0]
    new_secondary_domain_switch = failoversNuevos[1]
    response = client.change_resource_record_sets(
    ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Failover': 'PRIMARY',
                        # Se creo healtcheck para este subdominio que apunta a API de prueba.
                        'HealthCheckId': '7c6cde53-9f1f-4ec7-acf3-bb5b301ca911',
                        'Name': production_domain,
                        'ResourceRecords': [
                            {
                                'Value': new_primary_domain_switch,
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
                        # El secundario no debe usar Health check. Para cuando esté sano el primero se regrese nuevamente.
                        'HealthCheckId': '-',
                        'Name': production_domain,
                        'ResourceRecords': [
                            {
                                'Value': new_secondary_domain_switch,
                            },
                        ],
                        'SetIdentifier': 'DR region',
                        'TTL': 60,
                        'Type': 'CNAME',
                    },
                },
            ],
            'Comment': 'Failover Produccion a DR',
        },
        HostedZoneId=hosted_zone_id,
    )
switch()

print("#############################################")
print("LOS VALORES EN ROUTE 53 SE HAN ACTUALIZADO...")
print("OBTENIENDO VALORES NUEVOS...")
print("#############################################")
obtenerDominios()

