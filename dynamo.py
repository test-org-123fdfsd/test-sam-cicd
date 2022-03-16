import os
import sys
import time
from operator import truediv

import boto3
import pandas
import numpy as np

# El profile_name se debe eliminar previo a la implementación en workflow.
session = boto3.Session(profile_name="principal-dev", region_name="us-east-1")
dynamo = session.client("dynamodb")

# Aqui se cambiará ruta_tablas por tablas/ previo a la implementación en workflows
ruta_tablas = "/mnt/c/users/sps/Git-Repos/test-sam-cicd/tablas"

# Será necesario agregar variable de ambiente
nombre_tabla_estructura = "sia-gen-adm-estructura-catalogos-dev"
nombre_tabla_no_estructura = "sia-gen-adm-estructura-no-catalogos-dev"


def lista_csvs():
    """
    Función que crea una lista de todos los archivos dentro de la carpeta tablas/.

    A su vez, cambia la extensión por el nombre del ambiente donde vayan a ser
    insertados los valores.

    """
    from os import walk

    lista_tablas = next(walk(ruta_tablas), (None, None, []))[2]

    # El valor -pre se cambiaría por -${{env.samEnv}} previo a implementación en workflows
    lista_csvs.lista_tablas_ambiente = [w.replace(".csv", "") for w in lista_tablas]


lista_csvs()


def funcion_madre(nombre_tabla):
    """Controla el flujo de funciones que realizan la validación e inserción."""

    def validar_existencia_tablas(tablas):
        """Valida la existencia o inexistencia de las tablas."""

        lista_tablas_existentes = []
        lista_tablas_inexistentes = []

        for x in tablas:
            try:
                response = dynamo.describe_table(TableName=x)
                lista_tablas_existentes.append(x)
            except:
                # Se separan tablas inexistentes
                lista_tablas_inexistentes.append(x)

        if lista_tablas_existentes != []:
            print(
                "\n#------------------------------------------------------------------------#"
            )
            print("Tablas existentes: " + ", ".join(lista_tablas_existentes))
            print(
                "#---------------------------------------------------------------------------#"
            )

        if lista_tablas_inexistentes != []:
            print(
                "\n#-------------------------------------------------------------------------#"
            )
            print("Tablas inexistentes: " + ", ".join(lista_tablas_inexistentes))
            print(
                "#---------------------------------------------------------------------------#"
            )

    validar_existencia_tablas(lista_csvs.lista_tablas_ambiente)

    def existe_item(tablas_estructura):
        """Consulta la existencia de un valor en una tabla de dynamo."""

        print(
            "\n#-------------------------------------------------------------------------------#"
        )
        print(f"Validando existencia de item en: {tablas_estructura}")

        try:
            response = dynamo.query(
                ExpressionAttributeValues={
                    ":v1": {
                        "S": nombre_tabla,
                    },
                },
                KeyConditionExpression="NOMBRE = :v1",
                TableName=tablas_estructura,
            )

            query = response["Items"]

            if query != []:
                print(
                    f"Se encontró {nombre_tabla} listada en los items de la tabla: {tablas_estructura}"
                )
                existe_item.tablas_validadoras = dynamo.scan(
                    TableName=tablas_estructura
                )
                return True

            if query == []:
                print(
                    f"No se encontró {nombre_tabla} listada en los items de esta tabla."
                )
                return False

        except Exception as e:
            print(e)

    def validacion_existencia_item():
        """
        Función que ejecuta la función de existe_item recibiendo ambos nombres de las tablas de estructura.

        Esto lo hace con la finalidad de saber si el item de la tabla está registrado en alguna de las tablas de estructura.
        Caso contrario, se detiene la ejecución de este script.
        """

        if existe_item(nombre_tabla_estructura) == existe_item(
            nombre_tabla_no_estructura
        ):
            print(
                "\n!!------------------------------------------------------------------------!!"
            )
            print(
                f"No se encontró {nombre_tabla} en ninguna de las tablas de estructura."
            )
            print(
                "Favor de verificar la existencia de los items en la tabla correspondiente."
            )
            print(
                "!!--------------------------------------------------------------------------!!"
            )
            quit()

    validacion_existencia_item()

    def create_table(tablas):
        """AUN NO ESTÁ COMPLETADA. ES NECESARIO SEGUIR LA ESTRUCTURA."""
        """
        Función que crea tablas que no existan.
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
        CreateTable is an asynchronous operation. Upon receiving a CreateTable request,
        DynamoDB immediately returns a response with a TableStatus of CREATING .
        After the table is created, DynamoDB sets the TableStatus to ACTIVE .
        You can perform read and write operations only on an ACTIVE table.
        """
        for x in tablas:
            print("Intentando crear tabla")
            print(x)
            try:
                print("Creando tabla.. " + x)
                response = dynamo.create_table(
                    AttributeDefinitions=[
                        {"AttributeName": "ID", "AttributeType": "N"},
                    ],
                    TableName=x,
                    KeySchema=[
                        {"AttributeName": "ID", "KeyType": "HASH"},
                    ],
                    BillingMode="PAY_PER_REQUEST",
                    Tags=[
                        {"Key": "Proyecto", "Value": "SIA"},
                    ],
                )
                response = dynamo.describe_table(TableName=x)
                estado_tabla = response["Table"]["TableStatus"]
                while estado_tabla != "ACTIVE":
                    time.sleep(3)
                    response = dynamo.describe_table(TableName=x)
                    estado_tabla = response["Table"]["TableStatus"]
                    print(estado_tabla)
                print(f"Tabla {x} creada exitosamente")
            except:
                print("Error al intentar crear tabla.")

    # create_table(lista_tablas_inexistentes)

    def conversion_csv():
        """Función que permite convertir archivos csv en diccionarios."""

        print("Conversión CSV")
        df = pandas.read_csv(ruta_tablas + "/" + nombre_tabla + ".csv")

        # Se eliminan valores nulos a dataframe
        primer_renglon_todas_nan = df[df.isnull().all(axis=1) == True].index.tolist()[0]
        df = df.loc[0 : primer_renglon_todas_nan - 1]

        #Se reemplazan valores nan en dataframe.
        df = df.replace(to_replace=np.nan, value="")

        # Se convierte dataframe en diccionario.
        conversion_csv.diccionario_csv = df.to_dict()
        print("Termina conversión CSV")

    conversion_csv()

    def validador_estructura():
        """Crea un diccionario formado por la estructura a seguir de la tabla en cuestión."""

        validador_estructura.diccionarioValidador = {}
        result = None
        columnas_tipo_dato = 0

        while result is None:
            try:
                # Con esto obtenemos el tipo de dato dependiendo del nombre del campo

                validador_estructura.item_estructura = 0
                tabla = existe_item.tablas_validadoras["Items"][
                    validador_estructura.item_estructura
                ]["NOMBRE"]["S"]

                while tabla != nombre_tabla:
                    validador_estructura.item_estructura = (
                        validador_estructura.item_estructura + 1
                    )
                    tabla = existe_item.tablas_validadoras["Items"][
                        validador_estructura.item_estructura
                    ]["NOMBRE"]["S"]
                validador_estructura.item_estructura = (
                    validador_estructura.item_estructura
                )
                campo = existe_item.tablas_validadoras["Items"][
                    validador_estructura.item_estructura
                ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["campo"]["S"]
                tipo_dato = existe_item.tablas_validadoras["Items"][
                    validador_estructura.item_estructura
                ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["tipo"]["S"]
                print(validador_estructura.diccionarioValidador)
                validador_estructura.diccionarioValidador.update({campo: tipo_dato})
                columnas_tipo_dato = columnas_tipo_dato + 1
            except Exception as e:
                print(e)
                result = "OK"
                print("\n#-----------------------------#")
                print("Se concluyó captura de validación.")
                print("#-----------------------------#")

    validador_estructura()

    def impresion_llaves():
        print(
            "\n#-------------------------------------------------------------------------#"
        )
        print("Llaves de diccionario validador:")
        print(f"Total: {len(validador_estructura.diccionarioValidador.keys())}")
        print(validador_estructura.diccionarioValidador)
        print(
            "\n#-------------------------------------------------------------------------#"
        )
        print("Llaves de diccionario de CSV:")
        print(f"Total: {len(conversion_csv.diccionario_csv.keys())}")
        print(conversion_csv.diccionario_csv)
        print(
            "----------------------------------------------------------------------------#"
        )

    impresion_llaves()

    def validador_numero_columnas():
        """Valida el número de columnas del diccionario de estructura vs el diccionario validador."""

        if len(conversion_csv.diccionario_csv.keys()) > len(
            validador_estructura.diccionarioValidador.keys()
        ):
            print("\nError...")
            print(
                '''
                El número de columnas es MAYOR a la tabla de estructura.
                Actualizar tabla de estructura antes.
                '''
            )
            quit()
        elif len(conversion_csv.diccionario_csv.keys()) < len(
            validador_estructura.diccionarioValidador.keys()
        ):
            print("\nError...")
            print(
                '''
                El número de columnas es MENOR a la tabla de estructura.
                Actualizar tabla de estructura antes.
                '''
            )
            quit()

    validador_numero_columnas()

    def lectura_diccionarios():
        """Convierte los diccionarios en listas para leer columnas, filas y profundidad de los csv."""

        # - - - - Lista de valores que se insertarán.
        lectura_diccionarios.encabezadosCSV = []
        lectura_diccionarios.filasCSV = []
        lectura_diccionarios.profundidad = []

        for encabezado, fila in conversion_csv.diccionario_csv.items():
            lectura_diccionarios.encabezadosCSV.append(encabezado)
            lectura_diccionarios.filasCSV.append(fila)
            for profundidad in fila:
                lectura_diccionarios.profundidad.append(profundidad)

        # - - - - Lista diccionario que validará.
        lectura_diccionarios.valoresValidadores = []
        lectura_diccionarios.llavesValidadores = []

        for llave, valores in validador_estructura.diccionarioValidador.items():
            lectura_diccionarios.llavesValidadores.append(llave)
            lectura_diccionarios.valoresValidadores.append(valores)

        # Se elimina duplicidad de lista Profundidad.
        lectura_diccionarios.profundidad = list(
            dict.fromkeys(lectura_diccionarios.profundidad)
        )

    lectura_diccionarios()

    def obtener_llave_primaria():
        """Se obtiene la llave primaria desde la tabla de estructura correspondiente."""

        columnas_tipo_dato = 0
        obtener_llave_primaria.llave_primaria = existe_item.tablas_validadoras["Items"][
            validador_estructura.item_estructura
        ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["llavePrimaria"]["BOOL"]

        print(f"El bool es: {type(obtener_llave_primaria.llave_primaria)}")

        while obtener_llave_primaria.llave_primaria == False:
            columnas_tipo_dato = columnas_tipo_dato + 1
            obtener_llave_primaria.llave_primaria = existe_item.tablas_validadoras[
                "Items"
            ][validador_estructura.item_estructura]["ESTRUCTURA"]["L"][
                columnas_tipo_dato
            ][
                "M"
            ][
                "llavePrimaria"
            ][
                "BOOL"
            ]

        obtener_llave_primaria.llave_primaria = existe_item.tablas_validadoras["Items"][
            validador_estructura.item_estructura
        ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["campo"]["S"]

        print(f"La llave primaria es: {obtener_llave_primaria.llave_primaria}")

    obtener_llave_primaria()

    def validador_nombre_columnas():
        """
        Valida que el nombre de las columnas coincida.

        Ordena las listas de los encabezados del csv y de la tabla de estructura
        y verifica que sus nombres coincidan. Caso contrario se detiene la ejecución
        del script.
        """

        # Se ordenan las listas antes de convertirse a string
        validador_nombre_columnas.llaves = sorted(
            lectura_diccionarios.llavesValidadores
        )
        validador_nombre_columnas.encabezados = sorted(
            lectura_diccionarios.encabezadosCSV
        )
        validador_nombre_columnas.llaves.insert(
            0,
            validador_nombre_columnas.llaves.pop(
                validador_nombre_columnas.llaves.index(
                    obtener_llave_primaria.llave_primaria
                )
            ),
        )
        validador_nombre_columnas.encabezados.insert(
            0,
            validador_nombre_columnas.encabezados.pop(
                validador_nombre_columnas.encabezados.index(
                    obtener_llave_primaria.llave_primaria
                )
            ),
        )
        print(validador_nombre_columnas.llaves)
        print(validador_nombre_columnas.encabezados)

        print(
            "\n---------------------------------------------------------------------------#"
        )
        print("Las llaves validadoras son: " + str(validador_nombre_columnas.llaves))
        print("----------------------------#")
        print(
            "Los encabezados del CSV son: " + str(validador_nombre_columnas.encabezados)
        )
        print("\n")

        if validador_nombre_columnas.llaves != validador_nombre_columnas.encabezados:
            print("Las llaves no coinciden")
            quit()
        print("Las llaves coinciden. Se continúa proceso.")
        print(
            "---------------------------------------------------------------------------#"
        )

    validador_nombre_columnas()

    def insercion():
        '''Crea el diccionario a insertarse y ejecuta la inserción.

        Forma un diccionario basado en los encabezados, filas y profundidad.
        A su vez se les asigna el tipo de dato correspondiente a cada columna.
        Al finalizar, utiliza el método put_item por cada fila del csv

        '''

        item_a_insertar = {}

        longitud_encabezado = len(validador_nombre_columnas.encabezados)
        longitud_profundidad = len(lectura_diccionarios.profundidad)

        print(f"Total de elementos a insertarse: {longitud_profundidad}")
        print(
            "#--------------------------------------------------------------------------------#"
        )
        inserciones = 0
        print(
            "#------------------------COMENZANDO INSERCIÓN.-------------------------------#"
        )
        while inserciones != longitud_profundidad:

            contador_listas = 0

            while contador_listas != longitud_encabezado:

                valor = lectura_diccionarios.filasCSV[contador_listas][inserciones]

                atributo = validador_nombre_columnas.encabezados[contador_listas]

                # Del diccionario validador se obtienen los tipos de dato correspondientes.
                tipo_dato = validador_estructura.diccionarioValidador

                item_a_insertar[atributo] = {tipo_dato[atributo]: str(valor)}

                contador_listas = contador_listas + 1

                if contador_listas == longitud_encabezado:
                    print("Diccionario a insertar:")
                    print(item_a_insertar)

                    # ------------------Inserción de valores en DYNAMO
                    response = dynamo.put_item(
                        TableName=nombre_tabla, Item=item_a_insertar
                    )
                    response
                    print("Inserción #" + str(inserciones + 1) + " completada.")

            inserciones = inserciones + 1

        print(
            "#-------------------------FIN DE INSERCION.----------------------------------#"
        )

    insercion()


# Ejecución uno por uno del proceso de tablas.
for nombres_tablas in lista_csvs.lista_tablas_ambiente:
    funcion_madre(nombres_tablas)
