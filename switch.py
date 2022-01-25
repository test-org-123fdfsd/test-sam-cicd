from asyncio.unix_events import BaseChildWatcher
from lib2to3.pgen2 import driver
import argparse
import os
import sys

import boto3
import time
import argparse
global args


client = boto3.client('route53')

# Failover Principal

# Se obtienen las variables parseadas
parser = argparse.ArgumentParser()

# Dominio primario
parser.add_argument(
    "-pd",
    "--primary-domain",
    required=True,
    action="store",
    dest="primary_domain",
    help="Primary domain.",
    default=None,
)
# Target primario
parser.add_argument(
    "-pt",
    "--primary-target",
    required=True,
    action="store",
    dest="primary_target",
    help="Primary target.",
    default=None,
)
# Dominio secundario
parser.add_argument(
    "-sd",
    "--secondary-domain",
    required=True,
    action="store",
    dest="failover_domain",
    help="Failover domain. DR environment.",
    default=None,
)
# Target secundario
parser.add_argument(
    "-st",
    "--secondary-target",
    required=True,
    action="store",
    dest="failover_target",
    help="Failover target of Route 53. DR.",
    default=None,
)
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

primary_domain = args.primary_domain
primary_target = args.primary_target

failover_domain = args.failover_domain
failover_target = args.failover_target


# Imprimimos los valores CNAME hacia adonde apunta.
print("El dominio " + primary_domain + " actualmente apunta a: " + primary_target)
print("El dominio " + failover_domain + " actualmente apunta a: " + failover_target)

# Conversión de valores de los dominios. Aquí se invierten entre ellos sus valores actuales.
temp_primary_domain = primary_domain
temp_failover_domain = failover_domain

new_primary_domain = temp_failover_domain
new_failover_domain = temp_primary_domain

print(f"Nuevo primario {" ".join(new_primary_domain)}")
print(f"Nuevo failover {" ".join(new_failover_domain)}")

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

# Se ejecuta función para switch.
response = client.change_resource_record_sets(
    ChangeBatch=records,
    HostedZoneId=hosted_zone_id,
)

print(response)
