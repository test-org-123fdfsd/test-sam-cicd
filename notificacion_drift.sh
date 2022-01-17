#!/bin/bash
# Dependiendo del estado de drift actual se imprimen los mensajes correspondientes.
if [[ $DRIFTSTATUS = "IN_SYNC" ]]; then MENSAJEDRIFT=$"no tiene DRIFTS."; \
elif [[ $DRIFTSTATUS = "DRIFTED" ]]; then MENSAJEDRIFT=$"tiene modificaciones manuales. Para mayor información visitar directamente Cloudformation."; \
elif [[ $DRIFTSTATUS = "DETECTION_FAILED" ]]; then MENSAJEDRIFT=$"verifica que el usuario de GitHub tenga permisos suficientes para los recursos del Stack."; \
elif [[ $DRIFTSTATUS = "NOT_CHECKED" ]]; then echo "aún no tiene listo el estatus. Verificar en CloudFormation."; fi
STACKS=$"El Stack"

curl -H 'Content-Type: application/json' \
          --retry 4 \
          --retry-delay 1 \
          -d '{"text": "'"$DRIFTSTATUS"' - '"$STACKS"' - '"$PREFIX-$STACK_NAME"' - '"$MENSAJEDRIFT"'"}' \
          https://mxspsolutions.webhook.office.com/webhookb2/a84b113f-9d27-4138-84ae-e3e4ab4830f2@ac5349df-152e-486f-9b39-fe3c4a25efe0/IncomingWebhook/e2f3db57ac59459a938f44c822548b89/10ed5eda-9b70-4598-858a-e5ae6599fa66