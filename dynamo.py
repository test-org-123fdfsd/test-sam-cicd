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
    '''Función que valida la existencia del item en ambas tablas de estructura.'''

    print("\n#--------------------------------")
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
    except Exception as e:
        print(e)
                    
existe_item(nombre_tabla_estructura)
existe_item(nombre_tabla_no_estructura)
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
def conv_csv():
    '''Función que permite convertir archivos csv en diccionarios.'''
    
    df = pandas.read_csv(ruta_tablas + '/' + nombre_tabla + '.csv')
    #Se eliminan valores nulos a dataframe
    primer_renglon_todas_nan = df[df.isnull().all(axis=1) == True].index.tolist()[0]
    df = df.loc[0:primer_renglon_todas_nan-1]
    #Se convierte dataframe en diccionario.
    conv_csv.data_dict = df.to_dict()
conv_csv()
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
            campo = tabla_no_estructura['Items'][0]['ESTRUCTURA']['L'][x]['M']["campo"]['S']
            tipo_dato = tabla_no_estructura['Items'][0]['ESTRUCTURA']['L'][x]['M']['tipo']['S']
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
    print("KEYS de diccionario validador:")
    print(f'Total: {len(validador_estructura.diccionarioValidador.keys())}')
    print(validador_estructura.diccionarioValidador)
    print("\n#--------------------------------------------------------------------------------#")
    print("KEYS de diccionario de CSV:")
    print(f'Total: {len(conv_csv.data_dict.keys())}')
    print(conv_csv.data_dict)
    print("--------------------------------------------------------------------------------#")
impresion_llaves()
#-----------------------------REPORTE DE LLAVES.------------------------------------#
#-------------------------------VALIDACIÓN DE NÚMERO DE COLUMNAS.------------------------------------#
def validador_numero_columnas():
    '''
    Esta función realiza la validación del número de columnas del diccionario de estructura
    contra el diccionario validador.
    '''

    if len(conv_csv.data_dict.keys()) > len(validador_estructura.diccionarioValidador.keys()):
        print("\nError...")
        print("El número de columnas es MAYOR a la tabla de estructura. Actualizar tabla de estructura antes.")
        sys.exit(0)
    elif len(conv_csv.data_dict.keys()) < len(validador_estructura.diccionarioValidador.keys()):
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

# - - - - Lista de valores que se insertarán. INICIO
    lectura_diccionarios.encabezadosCSV = []
    lectura_diccionarios.filasCSV = []
    lectura_diccionarios.profundidad = []
    for x, y in conv_csv.data_dict.items():
        lectura_diccionarios.encabezadosCSV.append(x) 
        lectura_diccionarios.filasCSV.append(y)
        for z in y:
            lectura_diccionarios.profundidad.append(z)
    # - - - - Lista de valores que se insertarán. FIN

    # - - - - Lista diccionario que validará. INICIO
    lectura_diccionarios.valoresValidadores = []
    lectura_diccionarios.llavesValidadores = []
    for x, y in validador_estructura.diccionarioValidador.items():
        lectura_diccionarios.llavesValidadores.append(x) 
        lectura_diccionarios.valoresValidadores.append(y)
    
    #Se elimina duplicidad de lista Profundidad.
    lectura_diccionarios.profundidad = list(dict.fromkeys(lectura_diccionarios.profundidad))
lectura_diccionarios()
#------------------------------DECLARACIÓN DE LISTAS DE COLUMNAS, FILAS Y PROFUNDIDAD.------------------------------------#

#-------------------------------VALIDACIÓN DE NOMBRE COLUMNAS.------------------------------------#
def validador_nombre_columnas():
    '''Esta función valida que el nombre de las columnas coincida.'''

    print("\n--------------------------------------------------------------------------------#")
    print("Las llaves validadoras son: " + str(lectura_diccionarios.llavesValidadores))
    print("--------------------------------------------------------------------------------#")
    print("Los encabezados del CSV son: " + str(lectura_diccionarios.encabezadosCSV))
    print("--------------------------------------------------------------------------------#")

    if lectura_diccionarios.llavesValidadores != lectura_diccionarios.encabezadosCSV:
        print("Las llaves no coinciden")    
        sys.exit(0)
    print("Las llaves se han validado exitosamente...")
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
    z = 0
    print("#------------------------COMENZANDO INSERCIÓN.------------------------------------#")
    while z != longitud_profundidad:
        x = 0
        while x != longitud_encabezado:
            valor = lectura_diccionarios.filasCSV[x][z]
            tipo_dato = lectura_diccionarios.valoresValidadores[x]
            item_a_insertar[lectura_diccionarios.encabezadosCSV[x]] = {tipo_dato: str(valor)}
            ########VALIDACIÓN DE ESTRUCTURA FORMADA
            x = x + 1
            if x == longitud_encabezado:
                #------------------Inserción de valores en DYNAMO
                response = dynamo.put_item(
                TableName=nombre_tabla,
                Item=item_a_insertar)
                response
                print("Inserción #" + str(z + 1) + " completada.")
        z = z + 1
    print("#-------------------------FIN DE INSERCION.---------------------------------------#")
insercion()

#-----------------------------CREACIÓN DE DICCIONARIO A INSERTAR EN PUT_ITEM------------------------------------#
