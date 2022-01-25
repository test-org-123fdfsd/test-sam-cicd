#!/bin/bash

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -hz|--hostedzone) HOSTEDZONEID="$2"; shift ;;
        -pd|--primary-domain) PRIMARY_DOMAIN="$2"; shift ;;
        -fd|--failover-domain) FAILOVER_DOMAIN="$2"; shift ;;
    esac
    shift
done

# Obtener valor de CNAME de dominio Principal.
PRIMARY_TARGET=$(aws route53 list-resource-record-sets --hosted-zone-id ${HOSTEDZONEID} --query "ResourceRecordSets[?Name == '${PRIMARY_DOMAIN}.']" \
| jq '.[].ResourceRecords[].Value')
PRIMARY_TARGET=$(echo "${PRIMARY_TARGET//'"'}")
echo "El dominio " $PRIMARY_DOMAIN " actualmente apunta a: " $PRIMARY_TARGET)

# Obtener valor de CNAME Failover
FAILOVER_TARGET=$(aws route53 list-resource-record-sets --hosted-zone-id ${HOSTEDZONEID} --query "ResourceRecordSets[?Name == '${FAILOVER_DOMAIN}.']" \
| jq '.[].ResourceRecords[].Value')
FAILOVER_TARGET=$(echo "${FAILOVER_TARGET//'"'}")
echo "El dominio " $FAILOVER_DOMAIN " actualmente apunta a: " $FAILOVER_TARGET)