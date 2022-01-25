from asyncio.unix_events import BaseChildWatcher
from lib2to3.pgen2 import driver
import boto3
import argparse
global args

client = boto3.client('route53')

# Necesitamos el ID de la hosted zone del dominio.
# Se puede obtener con el comando:

# Primero listamos las zonas desde el AWS CLI con el comando: aws route53 list-hosted-zones

# El ID que nos interesa es el que comienza con Z (ej. Z08055123G7EJOFJG8E8F)

# Esqueleto 
''' response = client.change_resource_record_sets(
    HostedZoneId='string',
    ChangeBatch={
        'Comment': 'string',
        'Changes': [
            {
                'Action': 'CREATE'|'DELETE'|'UPSERT',
                'ResourceRecordSet': {    
                    # Nombre del string [Obligatorio] 
                    'Name': 'string',

                    # Tipo de redirección [Obligatorio]
                    'Type': 'SOA'|'A'|'TXT'|'NS'|'CNAME'|'MX'|'NAPTR'|'PTR'|'SRV'|'SPF'|'AAAA'|'CAA'|'DS', 

                    # Routing Policy en caso de que no sea simple, por ejemplo: Weighted, Geolocation, Failover, etc. [Obligatoria]  
                    'SetIdentifier': 'string',    

                    # Solo aplica cuando el Routing Policy es Weighted. 
                    'Weight': 123,
                    
                    # Solo aplica cuando la Routing Policy es basado en latencia.
                    'Region': 'us-east-1'|'us-east-2'|'us-west-1'|'us-west-2'|'ca-central-1'|'eu-west-1'|'eu-west-2'|'eu-west-3'|'eu-central-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-southeast-3'|'ap-northeast-1'|'ap-northeast-2'|'ap-northeast-3'|'eu-north-1'|'sa-east-1'|'cn-north-1'|'cn-northwest-1'|'ap-east-1'|'me-south-1'|'ap-south-1'|'af-south-1'|'eu-south-1',
                    
                    # Solo aplica cuando la Routing Policy es basado en Geolocalation.
                    'GeoLocation': {
                        'ContinentCode': 'string',
                        'CountryCode': 'string',
                        'SubdivisionCode': 'string'
                    },

                    # Solo aplica cuando la Routing Policy es basado es Failover.
                    'Failover': 'PRIMARY'|'SECONDARY',

                    # Solo aplica cuando la Routing Policy es basado MultiValueAnswer 
                    'MultiValueAnswer': True|False,
                    'TTL': 123,
                    'ResourceRecords': [
                        {
                            'Value': 'string'
                        },
                    ],
                    # Esto es requerido cuando se va apuntar a un recurso de AWS. S3, Cloudfront, etc.
                    'AliasTarget': {
                        'HostedZoneId': 'string',
                        'DNSName': 'string',
                        'EvaluateTargetHealth': True|False
                    },
                    'HealthCheckId': 'string',
                    'TrafficPolicyInstanceId': 'string'
                }
            },
        ]
    }
)
'''

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
    help="Primary domain. Prod environment.",
    default=None,
)
# Target primario
parser.add_argument(
    "-pt",
    "--primary-target",
    required=True,
    action="store",
    dest="primary_target",
    help="Primary target. Prod environment.",
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

# Cachamos los valores parseados
args = parser.parse_args()

primary_domain = args.primary_domain
primary_target = args.primary_target

failover_domain = args.failover_domain
failover_target = args.failover_target


# Imprimimos los valores CNAME hacia adonde apunta.
print("El dominio " + primary_domain + " actualmente apunta a: " + primary_target)
print("El dominio " + failover_domain + " actualmente apunta a: " + failover_target)

# Conversión de valores de los targets.
conv_primary_target = primary_target 
conv_failover_target = failover_target

primary_target = conv_failover_target
failover_target = conv_primary_target

# Se ejecuta función para switch.
response = client.change_resource_record_sets(
    ChangeBatch={
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Failover': 'PRIMARY',
                    # Se creo healtcheck para este subdominio
                    'HealthCheckId': 'a04de13d-00ea-408a-b0bf-f98aa7d3e948',
                    'Name': {primary_domain},
                    'ResourceRecords': [
                        {
                            'Value': {primary_target},
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
                    # 'HealthCheckId': 'a04de13d-00ea-408a-b0bf-f98aa7d3e948',
                    'Name': {failover_domain},
                    'ResourceRecords': [
                        {
                            'Value': {failover_target},
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
    HostedZoneId=${{ secrets.ROUTE53_HOSTEDZONEID }},
)

print(response)

# Imprimimos los valores CNAME hacia adonde apunta.
print("El dominio " + primary_domain + " actualmente apunta a: " + primary_target)
print("El dominio " + failover_domain + " actualmente apunta a: " + failover_target)