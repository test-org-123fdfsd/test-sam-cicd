from operator import truediv
import time
import pandas
import boto3
import sys

#------------------------------------VARIABLES------------------------------------#
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')

######Aqui se cambiará ruta_tablas por tablas/ previo a la implementación en workflows
ruta_tablas = "/mnt/c/users/sps/Git-Repos/test-sam-cicd/tablas"
nombre_tabla = 'test-dynamo-dev'
######Será necesario agregar variable de ambiente
nombre_tabla_estructura = 'sia-gen-adm-estructura-catalogos-dev'
tabla_estructura = dynamo.scan(TableName=nombre_tabla_estructura)
nombre_tabla_no_estructura = 'sia-gen-adm-estructura-no-catalogos-dev'
tabla_no_estructura = dynamo.scan(TableName=nombre_tabla_no_estructura)

#------------------------------------VARIABLES------------------------------------#

#-----------------------------------LISTA DE ARCHIVOS------------------------------------#
def lista_csvs():
    '''
    Función que crea una lista de todos los archivos dentro de la carpeta tablas/
    A su vez, cambia la extensión por el nombre del ambiente.
    '''
    from os import walk
    lista_tablas = next(walk(ruta_tablas), (None, None, []))[2]
    #### El valor -pre se cambiaría por -${{env.samEnv}} previo a implementación en workflows
    lista_csvs.lista_tablas_ambiente = [w.replace('.csv', '') for w in lista_tablas]
lista_csvs()
#-----------------------------------LISTA DE ARCHIVOS------------------------------------#

#-------------------Validación de existencia de tablas y separación en listas.
#-----------------------------TABLAS EXISTENTES E INEXISTENTES.------------------------------------#
def validar_existencia_tablas(tablas):
    '''Función que nos permite validar la existencia o inexistencia de las tablas'''
    lista_tablas_existentes = []
    lista_tablas_inexistentes = []
    for x in tablas:
        try:
            response = dynamo.describe_table(
            TableName=x)
            lista_tablas_existentes.append(x)
        except:
            # Se separan tablas inexistentes
            lista_tablas_inexistentes.append(x)
    if lista_tablas_existentes != []:
        print("\n#--------------------------------------------------------------------------------#")
        print('Tablas existentes: ' + ', '.join(lista_tablas_existentes))
        print("#--------------------------------------------------------------------------------#")
    if lista_tablas_inexistentes != []:
        print("\n#--------------------------------------------------------------------------------#")
        print('Tablas inexistentes: ' + ', '.join(lista_tablas_inexistentes))
        print("#--------------------------------------------------------------------------------#")
validar_existencia_tablas(lista_csvs.lista_tablas_ambiente)
#-----------------------------TABLAS EXISTENTES E INEXISTENTES.------------------------------------#
#-----------------------------VALIDACIÓN EXISTENCIA DE ITEM EN TABLAS DE ESTRUCTURA----------------#
def existe_item(tablas_estructura):
    '''Función que consulta la existencia de un valor en una tabla de dynamo.'''

    print("\n#-------------------------------------------------------------------------------#")
    print(f'Validando existencia de item en: {tablas_estructura}')
    try:
        response = dynamo.query(

            ExpressionAttributeValues={
            ':v1': {
                'S': nombre_tabla,
            },
            },
            KeyConditionExpression='NOMBRE = :v1',
            TableName=tablas_estructura,
            )
        query = response["Items"]
        if query != []:
            print(f'Se encontró tabla listada en los items de la tabla: {tablas_estructura}')
        if query == []:
            print("No se encontró tabla listada en los items de esta tabla.")
            return True
    except Exception as e:
        print(e)

def validacion_existencia_item():
    '''
    Función que ejecuta la función de existe_item recibiendo ambos nombres de las tablas de estructura.
    Con la finalidad de saber si el item de la tabla está registrado en alguna de las tablas de estructura.
    Caso contrario, se detiene la ejecución de este script.
    '''
    if existe_item(nombre_tabla_estructura) == existe_item(nombre_tabla_no_estructura):
        print("\n!!-----------------------------------------------------------------------------------!!")
        print(f'No se encontró {nombre_tabla} en ninguna de las tablas de estructura.')
        print("Favor de verificar la existencia de los items en la tabla correspondiente.")
        print("!!-----------------------------------------------------------------------------------!!")
        sys.exit(0)
validacion_existencia_item()

#------------------------------EXISTE ITEM------------------------------------#
#------------------------------CREAR TABLAS------------------------------------#
def create_table(tablas):
    '''AUN NO ESTÁ COMPLETADA. ES NECESARIO SEGUIR LA ESTRUCTURA.'''
    '''
    Función que crea tablas que no existan.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
    CreateTable is an asynchronous operation. Upon receiving a CreateTable request, 
    DynamoDB immediately returns a response with a TableStatus of CREATING . 
    After the table is created, DynamoDB sets the TableStatus to ACTIVE . 
    You can perform read and write operations only on an ACTIVE table.
    '''
    for x in tablas:
        print("Intentando crear tabla")
        print(x)
        try:
            print("Creando tabla.. " + x)                        
            response = dynamo.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'ID',
                        'AttributeType': 'N'
                    },
                ],
                TableName=x,
                KeySchema=[
                    {
                        'AttributeName': 'ID',
                        'KeyType': 'HASH'
                    },
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {
                        'Key': 'Proyecto',
                        'Value': 'SIA'
                    },
                ]
            )
            response = dynamo.describe_table(TableName=x)
            estado_tabla = response['Table']['TableStatus']
            while estado_tabla != 'ACTIVE':
                time.sleep(3)
                response = dynamo.describe_table(TableName=x)
                estado_tabla = response['Table']['TableStatus']                                           
                print(estado_tabla)
            print(f'Tabla {x} creada exitosamente')
        except:
            print("Error al intentar crear tabla.")
#create_table(lista_tablas_inexistentes)

#-----------------------------CONVERSIÓN DE CSV A DICCIONARIO.------------------------------------#
def conversion_csv():
    '''Función que permite convertir archivos csv en diccionarios.
    '''
    
    df = pandas.read_csv(ruta_tablas + '/' + nombre_tabla + '.csv')
    #Se eliminan valores nulos a dataframe
    primer_renglon_todas_nan = df[df.isnull().all(axis=1) == True].index.tolist()[0]
    df = df.loc[0:primer_renglon_todas_nan-1]
    #Se convierte dataframe en diccionario.
    conversion_csv.diccionario_csv = df.to_dict()
conversion_csv()
#-----------------------------CONVERSIÓN DE CSV A DICCIONARIO.------------------------------------#

#-----------------------------GENERACIÓN DE DICCIONARIO VALIDADOR.------------------------------------#
def validador_estructura():
    '''
    Esta función permite crear un diccionario formado por 
    la estructura a seguir de la tabla en cuestión.
    '''
    validador_estructura.diccionarioValidador = {}
    result = None
    x = 0
    while result is None:
        try:
            # Con esto obtenemos el tipo de dato dependiendo del nombre del campo
            #!!!!CAMBIAR 0 por nombre de tabla a validar!!!!
            # Se agregará for para encontrar el nombre de la tabla en la lista.
            item_estructura = 0
            tabla = tabla_no_estructura['Items'][item_estructura]['NOMBRE']['S']
            while tabla != nombre_tabla:
                item_estructura = item_estructura + 1
            campo = tabla_no_estructura['Items'][item_estructura]['ESTRUCTURA']['L'][x]['M']["campo"]['S']
            tipo_dato = tabla_no_estructura['Items'][item_estructura]['ESTRUCTURA']['L'][x]['M']['tipo']['S']
            validador_estructura.diccionarioValidador
            validador_estructura.diccionarioValidador.update({campo: tipo_dato})
            x = x + 1
        except:
            result = 'OK'
            print("\n#-----------------------------#")
            print("Se concluyó captura de validación.")
            print("#-----------------------------#")
validador_estructura()
#-----------------------------GENERACIÓN DE DICCIONARIO VALIDADOR.------------------------------------#

#-----------------------------REPORTE DE LLAVES.------------------------------------#
def impresion_llaves():
    print("\n#--------------------------------------------------------------------------------#")
    print("Llaves de diccionario validador:")
    print(f'Total: {len(validador_estructura.diccionarioValidador.keys())}')
    print(validador_estructura.diccionarioValidador)
    print("\n#--------------------------------------------------------------------------------#")
    print("Llaves de diccionario de CSV:")
    print(f'Total: {len(conversion_csv.diccionario_csv.keys())}')
    print(conversion_csv.diccionario_csv)
    print("--------------------------------------------------------------------------------#")
impresion_llaves()
#-----------------------------REPORTE DE LLAVES.------------------------------------#
#-------------------------------VALIDACIÓN DE NÚMERO DE COLUMNAS.------------------------------------#
def validador_numero_columnas():
    '''
    Esta función realiza la validación del número de columnas del diccionario de estructura
    contra el diccionario validador.
    '''

    if len(conversion_csv.diccionario_csv.keys()) > len(validador_estructura.diccionarioValidador.keys()):
        print("\nError...")
        print("El número de columnas es MAYOR a la tabla de estructura. Actualizar tabla de estructura antes.")
        sys.exit(0)
    elif len(conversion_csv.diccionario_csv.keys()) < len(validador_estructura.diccionarioValidador.keys()):
        print("\nError...")
        print("El número de columnas es MENOR a la tabla de estructura. Actualizar tabla de estructura antes.")
        sys.exit(0)
validador_numero_columnas()
#-------------------------------VALIDACIÓN DE NÚMERO DE COLUMNAS.------------------------------------#

#------------------------------DECLARACIÓN DE LISTAS DE COLUMNAS, FILAS Y PROFUNDIDAD.------------------------------------#
def lectura_diccionarios():
    '''
    Esta función convierte los diccionarios en listas con la finalidad de poder leer por completo
    todas las columnas, filas y profundidad de las columnas.
    '''
# - - - - Lista de valores que se insertarán.
    lectura_diccionarios.encabezadosCSV = []
    lectura_diccionarios.filasCSV = []
    lectura_diccionarios.profundidad = []
    for encabezado, fila in conversion_csv.diccionario_csv.items():
        lectura_diccionarios.encabezadosCSV.append(encabezado) 
        lectura_diccionarios.filasCSV.append(fila)
        for profundidad in fila:
            lectura_diccionarios.profundidad.append(profundidad)
    # - - - - Lista de valores que se insertarán.

    # - - - - Lista diccionario que validará.
    lectura_diccionarios.valoresValidadores = []
    lectura_diccionarios.llavesValidadores = []
    for llave, valores in validador_estructura.diccionarioValidador.items():
        lectura_diccionarios.llavesValidadores.append(llave) 
        lectura_diccionarios.valoresValidadores.append(valores)
    
    #Se elimina duplicidad de lista Profundidad.
    lectura_diccionarios.profundidad = list(dict.fromkeys(lectura_diccionarios.profundidad))
lectura_diccionarios()
#------------------------------DECLARACIÓN DE LISTAS DE COLUMNAS, FILAS Y PROFUNDIDAD.------------------------------------#

#-------------------------------VALIDACIÓN DE NOMBRE COLUMNAS.------------------------------------#
def validador_nombre_columnas():
    '''Esta función valida que el nombre de las columnas coincida.'''

    print("\n--------------------------------------------------------------------------------#")
    print("Las llaves validadoras son: " + str(lectura_diccionarios.llavesValidadores))
    print("----------------------------#")
    print("Los encabezados del CSV son: " + str(lectura_diccionarios.encabezadosCSV))
    print("\n")

    if lectura_diccionarios.llavesValidadores != lectura_diccionarios.encabezadosCSV:
        print("Las llaves no coinciden")    
        sys.exit(0)
    print("Las llaves coinciden. Se continúa proceso.")
    print("--------------------------------------------------------------------------------#")
validador_nombre_columnas()
#-------------------------------VALIDACIÓN DE NOMBRE COLUMNAS.------------------------------------#

#-----------------------------CREACIÓN DE DICCIONARIO A INSERTAR EN PUT_ITEM------------------------------------#
def insercion():
    item_a_insertar = {}
    longitud_encabezado = len(lectura_diccionarios.encabezadosCSV)
    longitud_profundidad = len(lectura_diccionarios.profundidad)
    print(f'Total de elementos a insertarse: {longitud_profundidad}')
    print("#--------------------------------------------------------------------------------#")
    inserciones = 0
    print("#------------------------COMENZANDO INSERCIÓN.------------------------------------#")
    while inserciones != longitud_profundidad:
        contador_listas = 0
        while contador_listas != longitud_encabezado:
            valor = lectura_diccionarios.filasCSV[contador_listas][inserciones]
            tipo_dato = lectura_diccionarios.valoresValidadores[contador_listas]
            item_a_insertar[lectura_diccionarios.encabezadosCSV[contador_listas]] = {tipo_dato: str(valor)}
            contador_listas = contador_listas + 1
            if contador_listas == longitud_encabezado:
                #------------------Inserción de valores en DYNAMO
                response = dynamo.put_item(
                TableName=nombre_tabla,
                Item=item_a_insertar)
                response
                print("Inserción #" + str(inserciones + 1) + " completada.")
        inserciones = inserciones + 1
    print("#-------------------------FIN DE INSERCION.---------------------------------------#")
insercion()

#-----------------------------CREACIÓN DE DICCIONARIO A INSERTAR EN PUT_ITEM------------------------------------#
