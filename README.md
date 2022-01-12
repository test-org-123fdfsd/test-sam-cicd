# SIA-backend

Repositorio para el backend del Sistema Integral Automatizado.

## Interfaces
**Colocar definición de interfaz**

- Afore
- Fondos


## Diagrama de alto nivel
![Diagrama alto nivel](.img/diagrama.jpg)

## Tecnologías

- AWS SAM
- AWS Lambda
- AWS Cloudformation
- AWS API Gateway
- AWS Eventbridge
- AWS SQS

### SAM 

Para el desarrollo de las interfaces se utilizara SAM, un framework de AWS que permite el desarrollo de aplicaciones serverless de forma más sencilla, se puede considerar una extensión de CloudFormation así que al desplegar una aplicación SAM se crea un nuevo stack.

Soporta la creación de recursos de AWS que se utilizan comumente con Lambda al construir aplicaciones serverless, por ejemplo: DynamoDB, Eventos y API Gateway.

#### Instalación

- [SAM](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

- [AWS CLI](https://docs.aws.amazon.com/es_es/cli/latest/userguide/install-cliv2-windows.html#cliv2-windows-install)

- [Python 3.8](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe)

- [Pipx](https://pypa.github.io/pipx/)

- [Pyenv](https://github.com/pyenv-win/pyenv-win)

#### Recursos de SAM

SAM agrega nuevos recursos a CloudFormation:

-   [AWS::Serverless::Api](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html)
Crea una función lambda que recibe peticiones a traves del API Gateway, permite agregar un documento de OpenAPI para la configuración del API REST. [Comparación entre API REST y HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html)

-   [AWS::Serverless::Application](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-application.html)
Permite agregar una función lambda de [AWS Serverless Application Repository](https://serverlessrepo.aws.amazon.com/applications) o S3 a tu aplicación SAM.

-   [AWS::Serverless::Function](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html)
Crea una función lambda y un role de IAM asociado a ella. La función puede ser iniciada por distintos eventos (S3 | SNS | Kinesis | DynamoDB | SQS | Api | Schedule | CloudWatchEvent | EventBridgeRule | CloudWatchLogs | IoTRule | AlexaSkill)

-   [AWS::Serverless::HttpApi](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-httpapi.html)
Crea una función lambda que recibe peticiones a traves del API Gateway. [Comparación entre API REST y HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html)

-   [AWS::Serverless::LayerVersion](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-layerversion.html)
Si multiples funciones requieren las mismas librerías es posible crear una capa reutilizables que incluya estas librerías.


-   [AWS::Serverless::SimpleTable](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-simpletable.html)
Crea tablas de DynamoDB.


-   [AWS::Serverless::StateMachine](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-statemachine.html)
SAM también tiene soporte para agregar a tu proyecto Step Functions y mantener una base de código más ordenada.


#### Archivo template

Cada proyecto de SAM tiene un archivo template.yaml, en el se describen diversos recurso de AWS que son creados y utilizados por la aplicación.

En la siguiente liga se pueden encontrar algunos ejemplos de plantillas utilizando recurso de SAM:
https://serverlessland.com/patterns


No solo recursos de SAML pueden ser agregados, cualquier recurso de CloudFormation puede ser agregado al template.

En la siguiente liga se encuentran todos los recursos que pueden ser creados usando CloudFormation:
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html


#### AWS IDE Toolkits

AWS ofrece extensiones para distintos IDEs, los relevantes para este repositorio son:
- [Visual Studio Code](https://aws.amazon.com/visualstudiocode/)
- [PyCharm](https://aws.amazon.com/pycharm/)

Utilizar alguna de estas extensiones en tu IDE favorito te facilitará el desarrollo de aplicaciones SAM.

-----------------------------

## Configuración local


En esta sección encontrarás cómo configurar tu ambiente local.


### Pre-commit:

#### Prerequisitos:

### 1.	Instalar Python3.8

Opcional (https://github.com/pyenv-win/pyenv-win)

### 2.	Instalar pipx

Es recomendable actualizar pip antes de proseguir:
python -m pip install --upgrade pip

python -m pip install --user pipx
python -m pipx ensurepath

En caso de que se presenten problemas es recomendable:
  1. Agregar las rutas manualmente al PATH:

  C:\Users\NombredeUsuario\.local\bin
  C:\Users\NombredeUsuario\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts

  2. Reiniciar la consola.

### 3.	Instalar pre-commit
Estos comandos deben ejecutarse en el path del proyecto:


      pipx install pre-commit
      pre-commit --version


### 4. Instalar Commitizen
Se tiene que ejecutar en el path del proyecto:

      pipx install commitizen

### 5. Ejecutamos la instalación de Pre-commit
      pre-commit install

Una vez instalado haremos un commit “normal” inicial:

git commit -m “Inicializando pre-commit”

(Este proceso demorará algunos minutos debido a que se descargan los archivos necesarios. No interrumpir, por favor.)

### Archivos de configuración necesarios en la ruta del proyecto local ✨:

Plugin | Archivo
------------ | -------------
Pre-commit  |  .pre-commit-config.yaml
Commitizen  |  .cz.yaml
Flake8  |  .flake8
Isort  |  .isort.cfg

### Recomendaciones de Uso

Uso:
Cz commit
(se abrevia con el comando cz c)

1. Ingresamos el comando cz c para hacer commit con commitizen y seguimos las instrucciones:
2. Para la opción de "Proyecto" el autocompletar la podemos utilizar con la tecla tab
3. En caso de que uno de los plugins de pre-commit falle y ejecute una corrección en un archivo,
esos archivos deberán de volverse a agregar al stage.
4. Para no tener que volver a ingresar nuevamente el texto que pusimos en el commit podemos
usar el comando: cz c --retry

### Demos

![cz commit](.img/cz-commit.gif)


### Validador del nombrado de ramas
Recordemos lo previamente mencionado en nuestro Pull Request Template
Seguimos el estándar:


![](.img/estructura-estandar-ramas.png)
#### Ejemplo:

```

  utileria/ci-validador-nombrado-ramas-826

```
#### Rama que no sigue estándar
![Rama sin estándar](.img/rama_malnombrada.gif)
#### Aplicando estándar de nombrado a rama
![Rama con estándar](.img/rama_ok.gif)

#### Prueba anti hard code de región
![cz commit](.img/anti-hardcode-region.gif)
  
### Recursos

Validaciones de estándares de desarrollo - PGI PI Collaboratory Mex-Chi - PFG Confluence (principal.com)(https://docs.principal.com/pages/viewpage.action?pageId=589606389)

(Commitizen: https://commitizen-tools.github.io/commitizen/#integrating-with-pre-commit
repo: https://github.com/commitizen-tools/commitizen)


---------------------------------

#### Creación de una aplicación SAM

- Clonar el repositorio
- Abrir la terminal
- Moverse a la carpeta de negocio a la que pertenecera la aplicación SAM
- Crear aplicación utilizando el CLI de SAM

```
sam init
```
- Elegir la opción _1 - AWS Quick Start Templates_

- Elegir la opción _1 - Zip (artifact is a zip uploaded to S3)_

- Elegir la opción _2 - python3.8_

- Colocar el nombre de tu aplicación: {interfaz}-{tipo_aplicación}-{nombre}

Ejemplo:
```
md-stepfunction-ejemplo
```

Hay 5 plantillas de aplicación elegir la que más se adecua a tu proyecto.
Para Step Functions se utilizara la plantilla _4 - Step Functions Sample App (Stock Trader)_
Para una función que reaciona a un evento de eventbridge seleccionar _2 - EventBridge Hello World_
Para una función que se expone en el API Gateway seleccionar __1 - Hello World__


## Estructura del repositorio

```
SIA-backend/
├─afore/
│  └──workflows/
│     └─ {workflow}/
│        ├─ functions/
│        │   └─ {function_name}/
│        │      ├─ app.py
│        │      └─ requirements.txt
│        ├─ statemachine/
│        │  └─ {statemachine_name}.asl.json
│        ├─ tests/
│        ├─ template.yaml
│        └─ README.yaml
├─fondos/
│  └──workflows/
│     └─ {workflow}/
│        ├─ functions/
│        │   └─ {function_name}/
│        │      ├─ app.py
│        │      └─ requirements.txt
│        ├─ statemachine/
│        │  └─ {statemachine_name}.asl.json
│        ├─ tests/
│        ├─ template.yaml
│        └─ README.yaml
├─utileria/
│     ├─ {workflow}/
│     │  ├─ functions/
│     │  │  └─ {function_name}/
│     │  │      ├─ app.py
│     │  │      └─ requirements.txt
│     │  ├─ statemachine/
│     │  │  └─ {statemachine_name}.asl.json
│     │  ├─ tests/
│     │  ├─ template.yaml
│     │  └─ README.yaml
│     └─ sia-apigateway/
│        ├─ api-spec.yaml
│        └─ template.yaml
├─ README.md
├─ .github
└─ .gitignore
```

### {afore o fondos}/workflows
Esta carpeta contiene las maquinas de estados y funciones lambda que forman una interfaz.
El archivo template.yaml contiene los recursos que utiliza la interfaz state machine, SQS, S3, etc...

Si algún recurso (por ejemplo SQS) debe ser utilizado por más de una interfaz, se deberá mover al repositorio de plantillas: SAUTO_Templates

### {afore o fondos}/workflows/{nombre workflow}/functions
Funciones lambda que se utilizan en una interfaz.
Cada función contiene un archivo _requirements.txt_ con la lista de dependencias que utiliza. Si multiples funciones de un flujo utilizan las mismas librerías, se recomienda crear un _layer_.

El archivo _requirements.txt_ debe tener las dependencias fijadas (un número de versión definido).

Ejemplo:
```
requests==2.25.1
```

### utileria/workflows
Contiene funciones lambda o maquinas de estados que son utilizadas en otros flujos.

Estas funciones pueden ser llamadas directamente dentro de otra máquina de estados utilizando su nombre o su ARN:

```
{
   "StartAt":"CallLambda",
   "States":{
      "CallLambda":{
         "Type":"Task",
         "Resource":"arn:aws:states:::lambda:invoke",
         "Parameters":{
            "FunctionName":"MyFunction"
         },
         "End":true
      }
   }
}
```

También es posible utilizar otro servicio como SQS o EventBridge para desacoplar la función.

![lambda-sqs](.img/messaging0-1.png)


### utileria/sia-apigateway
Contiene la definición del API Gateway a utilizar por todas las interfaces. La recomendación es seguir una metodología API-first, así que el primer paso antes de exponer un nuevo recurso es agregar su definición a la especificación de Open API del API Gateway.

Ejemplo:
utileria/sia-apigateway/api-spec.yaml
```
paths:
  /hello:
    get:
      responses:
        '200':
          description: OK
          content:
            text/plain:
               schema:
                  type: string
                  example: hello
```

Puedes utilizar https://editor.swagger.io/ para editar la especificación.


Una vez se tiene la definición y se ha construido, se debe exportar el ARN de la función que servirá de API.

Ejemplo:
{afore o fondos}/workflows/{nombre workflow}/template.yaml
```
Outputs:
  HelloWorldFunction:
    Description: "Hello World Lambda Function ARN"
    Value: !GetAtt HelloWorldFunction.Arn
    Export:
      Name: "sia-afore-helloworld-api-arn"
```

El elemento Outputs.{Nombre Función}.Export.Name debe ser único en toda la cuenta de AWS. Se recomienda seguir el siguiente nombrado:
_sia-{negocio}-{funcion}-api-arn_

Ahora se deberá indicarle en la especificación de Open API que se debe llamar a nuestra función cuando se reciba una petición en el definición de recurso creada previamente.

Se debe colocar el siguiente fragmento dentro del elemento paths.{path}.{metodo} en el que se deberá ejecutar la función lambda. Se debe colocar el nombre del ARN exportado en el elemtno FN:ImportValue.

```
x-amazon-apigateway-integration:
  payloadFormatVersion: "2.0"
  type: "aws_proxy"
  httpMethod: "POST"
  uri:
    Fn::Join:
      - ''
      - - 'arn:aws:apigateway:'
        - Ref: 'AWS::Region'
        - ':lambda:path/2015-03-31/functions/'
        - Fn::ImportValue: {ARN exportado de la función}
        - '/invocations'
  connectionType: "INTERNET"
```

Ejemplo:

utileria/sia-apigateway/api-spec.yaml
```
paths:
  /hello:
    get:
      responses:
        '200':
          description: OK
          content:
            text/plain:
               schema:
                  type: string
                  example: hello
      x-amazon-apigateway-integration:
        payloadFormatVersion: "2.0"
        type: "aws_proxy"
        httpMethod: "POST"
        uri:
          Fn::Join:
            - ''
            - - 'arn:aws:apigateway:'
              - Ref: 'AWS::Region'
              - ':lambda:path/2015-03-31/functions/'
              - Fn::ImportValue: sia-afore-helloworld-api-arn
              - '/invocations'
        connectionType: "INTERNET"
```


### CI/CD
Se debera crear un workflow dentro de la carpeta .github del repositorio por cada aplicación SAM a desplegar.

El workflow deberá seguir el siguiente estandar de nombrado: _<negocio>-workflow-<nombre-aplicación>.yml_

El archivo workflow deberá tener el siguiente contenido:
**Pendiente - Actualizar en PR de CICD a nueva versión (con API Gateway y ambientes)**

```
on:
  push:
    branches:
      - develop
    paths:
      - "afore/workflows/sia-afore-ejemplo/**"
    workflow_dispatch:
jobs:
  deploy:
    defaults:
      run:
        working-directory: "afore/workflows/sia-afore-ejemplo/"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: aws-actions/setup-sam@v0
      - if: contains(github.ref, "develop")
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-2
      - if: contains(github.ref, "release")
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.PRE_AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.PRE_AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-2
      - if: contains(github.ref, "master")
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.PROD_AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.PROD_AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-2
      # Build inside Docker containers
      - run: sam build --use-container
      # Prevent prompts and failure when the stack is unchanged
      - run: |
          sam deploy \
          --no-confirm-changeset \
          --no-fail-on-empty-changeset \
          --stack-name sia-afore-ejemplo \
```

Se deberán modificar los siguiente valores de acuerdo al nombre de tu flujo
- on.push.paths: Remplazar por la ruta de tu proyecto de SAM
- jobs.deploy.defaults.run.working-directory: Remplazar con por la ruta de tu proyecto de SAM


## Flujo de trabajo de Git

Principal ha definido [Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) como el flujo de trabajo a utilizar en todos su proyectos.


## Tracing

Las funciones lambda permiten habilitar X-Ray para visualizar como interactua con otros componentes e identificar cuellos de botella.

![tracing](.img/sample-errorprocessor-servicemap.png)

Para habilitar el tracing ir la función en la consola de AWS
1. Seleccionar _Configuration_
2. Seleccionar _Monitoring Tools_
3. Seleccionar _Edit_
4. Marcar _Active_tracing_ en la sección de _x-Ray_
5. Seleccionar _Save_

Se agregará de forma automática el permiso necesario para enviar la información de tracing al rol de la función. En caso de que no ocurra se debe agregar manualmente el siguiente permiso al rol de la función: _AWSXRayDaemonWriteAccess_.

Si se desea medir cuanto tiempo tomo el llamado a funciones u otros servicios es posible hacerlo utilizando el SDK de X-Ray.

https://docs.aws.amazon.com/lambda/latest/dg/python-tracing.html
