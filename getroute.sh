#!/bin/bash

# Considerar volverse secretos. Estas son las variables a utilizar en este script.
HOSTEDZONEID=${{ secrets.ROUTE53_HOSTEDZONEID }}
PRIMARY_DOMAIN=${{ secrets.ROUTE53_PRIMARY_DOMAIN }}
FAILOVER_DOMAIN=${{ secrets.ROUTE53_FAILOVER_DOMAIN }}

# Obtener valor de CNAME de produccion.charlycloudy.com
PRIMARY_TARGET=$(aws route53 list-resource-record-sets --hosted-zone-id ${HOSTEDZONEID} --query "ResourceRecordSets[?Name == '${PRIMARY_DOMAIN}.']" \
| jq '.[].ResourceRecords[].Value')
PRIMARY_TARGET=$(echo "${PRIMARY_TARGET//'"'}")
echo $PRIMARY_TARGET

# Obtener valor de CNAME de disasterrecovery.charlycloudy.com
FAILOVER_TARGET=$(aws route53 list-resource-record-sets --hosted-zone-id ${HOSTEDZONEID} --query "ResourceRecordSets[?Name == '${FAILOVER_DOMAIN}.']" \
| jq '.[].ResourceRecords[].Value')
FAILOVER_TARGET=$(echo "${FAILOVER_TARGET//'"'}")
echo $FAILOVER_TARGET
