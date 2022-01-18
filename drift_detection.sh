#!/bin/bash
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--stackname) STACKNAME="$2"; shift ;;
    esac
    shift
done

# Se le quitan las comillas dobles a la variable de ambiente.
DRIFT=$(echo "${DRIFT//'"'}")

echo "El id de la deteccion del drift es:" $DRIFT

# A veces la detección del drift es larga, por lo cual podemos verificar 
# el estatus basado en su ID con el comando siguiente:

DETECTIONSTATUS=$(aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id ${DRIFT} | jq '.DetectionStatus')

# Se le quitan las comillas dobles a la variable de ambiente DETECTIONSTATUS
DETECTIONSTATUS=$(echo "${DETECTIONSTATUS//'"'}")

# El siguiente bucle verifica cada 2 segundos el estatus de la detección e imprime el estado actual. 
# Y no brinca al siguiente paso hasta que tenga un estado de: detección completada.

while [[ $DETECTIONSTATUS != "DETECTION_COMPLETE" ]]; do sleep 2; echo $DETECTIONSTATUS; \
DETECTIONSTATUS=$(aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id ${DRIFT} | jq '.DetectionStatus'); \
DETECTIONSTATUS=$(echo "${DETECTIONSTATUS//'"'}"); \
if [[ $DETECTIONSTATUS = "DETECTION_FAILED" ]]; then break; fi; \ 
done
echo $DETECTIONSTATUS

# Se muestra el estado actual del drift del stack 
DRIFTSTATUS=$(aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id $DRIFT | jq '.StackDriftStatus')
DRIFTSTATUS=$(echo "${DRIFTSTATUS//'"'}")
echo $DRIFTSTATUS


# Dependiendo del estado de drift actual se imprimen los mensajes correspondientes.
if [[ $DRIFTSTATUS = "DRIFTED" ]]; then MENSAJEDRIFT=$"tiene modificaciones manuales. Para mayor información visitar directamente Cloudformation."; \
elif [[ $DRIFTSTATUS = "DETECTION_FAILED" ]]; then MENSAJEDRIFT=$"verifica que el usuario de GitHub tenga permisos suficientes para los recursos del Stack."; \
elif [[ $DRIFTSTATUS = "NOT_CHECKED" ]]; then echo "aún no tiene listo el estatus. Verificar en CloudFormation."; fi
STACKS=$"El Stack"

if [[ $DRIFTSTATUS = "IN_SYNC" || $DRIFTSTATUS = "DETECTION_FAILED" || $DRIFTSTATUS = "NOT_CHECKED" ]]; then \
curl -H 'Content-Type: application/json' \
          --retry 4 \
          --retry-delay 1 \
          -d '{"text": "'"$DRIFTSTATUS"' - '"$STACKS"' - '"$STACK_NAME"' - '"$MENSAJEDRIFT"'"}' \
          https://mxspsolutions.webhook.office.com/webhookb2/a84b113f-9d27-4138-84ae-e3e4ab4830f2@ac5349df-152e-486f-9b39-fe3c4a25efe0/IncomingWebhook/e2f3db57ac59459a938f44c822548b89/10ed5eda-9b70-4598-858a-e5ae6599fa66; \
          fi