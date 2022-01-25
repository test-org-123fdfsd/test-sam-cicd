#!/bin/bash

# Considerar volverse secretos. Estas son las variables a utilizar en este script.
HOSTEDZONEID="${{env.hosted_zone_id}}"
PRIMARY_DOMAIN="${{env.primary_domain}}"
FAILOVER_DOMAIN="${{env.failover_domain}}"

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
