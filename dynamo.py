#1 Contar los archivos
#2 Listar los archivos
#3 Cambiar .csv por ambiente -${{env.samEnv}} a cada elemento de la lista.
#4 Validar si existen dichas tablas de la lista en AWS

############5 ¿Existen todas las tablas?
###########6.0 Si SÍ,  Imprimir Tablas por actualizar: <tablas-existentes>
###########6.1 Se usará la misma lista
###########6.2 Se entrará al contenido del csv de cada elemento de la lista
###########6.3 Se intentará hacer UPDATE a tabla

###########7.0 Si NO, Se separará la lista en 2. Tablas inexistentes y Tablas existentes
#7.1 Imprimir Tablas por actualizar: <tablas-existentes> y Tablas por crear: <tablas-no-existentes>

####7.2 ¿Qué lista es?
####Si es lista de tablas EXISTENTES
#7.3 SI es existente seguir pasos 6.1-6.3

####Si es lista de tablas INEXISTENTES
#8.0 Se entrará al contenido del csv de cada elemento de la lista
#8.1 Se intentará hacer un CREATE de la tabla    
#8.2 Se intentará hacer un INSERT/UPDATE a la tabla


#Creamos una función que sea CREATE_TABLE y dentro le ponemos un for en la lista de tablas EXISTENTES.

#Y otra función que sea UPDATE_TABLE y dentro el for en la lista de tablas EXISTENTES
