import time
import pandas
import boto3
import sys

#------------------------------------VARIABLES------------------------------------#
### El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name='principal-dev', region_name='us-east-1')
dynamo = session.client('dynamodb')

######Aqui se cambiará tablasPath por tablas/ previo a la implementación en workflows
tablasPath = "/mnt/c/users/sps/Git-Repos/test-sam-cicd/tablas"
nomTabla = 'test-dynamo-dev'
tablaEstructura = 'sia-gen-adm-estructura-no-catalogos-dev'
tablaEstructura = dynamo.scan(TableName=tablaEstructura)
#------------------------------------VARIABLES------------------------------------#

#-----------------------------------LISTA DE ARCHIVOS------------------------------------#
def lista_csvs():
    '''
    Función que crea una lista de todos los archivos dentro de la carpeta tablas/
    A su vez, cambia la extensión por el nombre del ambiente.
    '''
    from os import walk
    tablasLista = next(walk(tablasPath), (None, None, []))[2]
    #### El valor -pre se cambiaría por -${{env.samEnv}} previo a implementación en workflows
    lista_csvs.tablasListaEnv = [w.replace('.csv', '') for w in tablasLista]
lista_csvs()
#-----------------------------------LISTA DE ARCHIVOS------------------------------------#

#-------------------Validación de existencia de tablas y separación en listas.
#-----------------------------TABLAS EXISTENTES E INEXISTENTES.------------------------------------#
def validar_existencia_tablas(tablas):
    '''Función que nos permite validar la existencia o inexistencia de las tablas'''
    listaTablasExist = []
    listaTablasInexis = []
    for x in tablas:
        try:
            response = dynamo.describe_table(
            TableName=x)
            listaTablasExist.append(x)
        except:
            # Se separan tablas inexistentes
            listaTablasInexis.append(x)
    if listaTablasExist != []:
        print("\n#--------------------------------------------------------------------------------#")
        print('Tablas existentes: ' + ', '.join(listaTablasExist))
        print("#--------------------------------------------------------------------------------#")
    if listaTablasInexis != []:
        print("\n#--------------------------------------------------------------------------------#")
        print('Tablas inexistentes: ' + ', '.join(listaTablasInexis))
        print("#--------------------------------------------------------------------------------#")

validar_existencia_tablas(lista_csvs.tablasListaEnv)
#-----------------------------TABLAS EXISTENTES E INEXISTENTES.------------------------------------#

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
            tableStatus = response['Table']['TableStatus']
            while tableStatus != 'ACTIVE':
                time.sleep(3)
                response = dynamo.describe_table(TableName=x)
                tableStatus = response['Table']['TableStatus']                                           
                print(tableStatus)
            print(f'Tabla {x} creada exitosamente')
        except:
            print("Error al intentar crear tabla.")
#create_table(listaTablasInexis)

#-----------------------------CONVERSIÓN DE CSV A DICCIONARIO.------------------------------------#
def conv_csv():
    '''Función que permite convertir archivos csv en diccionarios.'''
    
    df = pandas.read_csv(tablasPath + '/' + nomTabla + '.csv')
    #Se eliminan valores nulos a dataframe
    first_row_with_all_NaN = df[df.isnull().all(axis=1) == True].index.tolist()[0]
    df = df.loc[0:first_row_with_all_NaN-1]
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
            campo = tablaEstructura['Items'][0]['ESTRUCTURA']['L'][x]['M']["campo"]['S']
            tipodato = tablaEstructura['Items'][0]['ESTRUCTURA']['L'][x]['M']['tipo']['S']
            validador_estructura.diccionarioValidador
            validador_estructura.diccionarioValidador.update({campo: tipodato})
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
    diccionarioAInsertar = {}
    longitudEnc = len(lectura_diccionarios.encabezadosCSV)
    longitudProf = len(lectura_diccionarios.profundidad)
    print(f'Total de elementos a insertarse: {longitudProf}')
    print("#--------------------------------------------------------------------------------#")
    z = 0
    print("#------------------------COMENZANDO INSERCIÓN------------------------------------#")
    while z != longitudProf:
        x = 0
        while x != longitudEnc:
            valor = lectura_diccionarios.filasCSV[x][z]
            tipodato = lectura_diccionarios.valoresValidadores[x]
            diccionarioAInsertar[lectura_diccionarios.encabezadosCSV[x]] = {tipodato: str(valor)}
            ########VALIDACIÓN DE ESTRUCTURA FORMADA
            x = x + 1
            if x == longitudEnc:
                #------------------Inserción de valores en DYNAMO
                response = dynamo.put_item(
                TableName=nomTabla,
                Item=diccionarioAInsertar)
                response
                print("Inserción #" + str(z + 1) + " completada.")
        z = z + 1
    print("#-------------------------FIN DE INSERCION---------------------------------------#")
insercion()

#-----------------------------CREACIÓN DE DICCIONARIO A INSERTAR EN PUT_ITEM------------------------------------#
