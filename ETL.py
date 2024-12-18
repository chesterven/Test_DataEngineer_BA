import pandas as pd 
import re
from datetime import datetime
import sqlite3
import logging


# Configurar el logger 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para insertar registro en BITACORA_PROCESOS 
def registrar_proceso(conn, id_proceso, nombre_proceso, estado): 
    fecha_ejecucion = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    cursor = conn.cursor() 
    cursor.execute("INSERT INTO BITACORA_PROCESOS (ID_PROCESO, NOMBRE_PROCESO, FECHA_EJECUCION, ESTADO) VALUES (?, ?, ?, ?)", (id_proceso, nombre_proceso, fecha_ejecucion, estado)) 
    conn.commit()


#Creamos metodo para limpiar los datos del nombre y DUI. 
def stage_limpieza(texto):

    #Log
    logging.info("Limpiando texto")

    # Eliminar caracteres especiales y números
    texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóú\s]', '', texto)
    
    # Reemplazar múltiples espacios en blanco por uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    return texto_limpio


#Creamos metodo para la clasificacion del nombre.
def clasificar_nombre_cliente(nombre_completo):

    #Log
    logging.info("Clasificando nombre")

    # Invocamos el metodo de limpieza previo a la trasnformacion.
    nombre_clean = stage_limpieza(nombre_completo)

    
    #Separamos en un arreglo llamado partes el nombre.
    partes = re.split(r'\s+', nombre_clean.strip())
     
    #Inicializamos variables/campos nuevos.
    nombre1, nombre2, nombre3 = '', '', ''
    apellido1, apellido2, casada = '', '', ''
    
    #Logica para la asignacion de valores en base al arreglo. 
    if len(partes) == 4 and 'de' not in partes:
        nombre1 = partes[0]
        nombre2 = partes[1]
        apellido1 = partes[-2]
        apellido2 = partes[-1]
    if len(partes) == 3 and 'de' not in partes:
        nombre1 = partes[0]
        nombre2 = partes[1]
        apellido1 = partes[-2]
    if len(partes) == 5 and 'de' not in partes:
        nombre1 = partes[0]
        nombre2 = partes[1]
        nombre3 = partes[2]
        apellido1 = partes[-2]
        apellido2 = partes[-1]
    if 'de' in partes:
        nombre1 = partes[0]
        nombre2 = partes[1]
        apellido1 = partes[-3]
        casada = partes[-2] + ' ' + partes[-1]
        
    
    return pd.Series([nombre1, nombre2, nombre3, apellido1, apellido2, casada])


# Inicializamos el dataframe con el archivo fuente

#log
logging.info("Conectando a la base de datos SQLite")

conn = sqlite3.connect('C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/ClientesListasBA.db')


#Bitacora BD
registrar_proceso(conn, 500001, 'Inicio del Proceso Carga Clientes', 'Iniciado')

#Log
logging.info("Leyendo archivo Excel")
df = pd.read_excel('C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/fuente.xlsx') 

# Invocacion de funcion de clasificacion de nombres
df[['Nombre1', 'Nombre2', 'Nombre3', 'Apellido1', 'Apellido2', 'Casada']] = df['Nombre'].apply(clasificar_nombre_cliente)

#Eliminamos la primera columna
df = df.iloc[:, 1:]

#Bitacora BD
registrar_proceso(conn, 500001, 'Finaliza del Proceso Trasnformacion', 'Finalizado')


#Nos coenctamos a la base de datos ClientesListasBA que fue proporcionada para la prueba

#Ejecutamos consultas sin filtros para obtener todos los registros de las tablas internas.

#log
logging.info("Leyendo las tablas clientes y lista_control")
df_sqlite_clientes = pd.read_sql_query('SELECT * FROM clientes', conn)
df_sqlite_control = pd.read_sql_query('SELECT * FROM lista_control', conn)

#Parametrizando el campo documento a tipo texto previo al cruce
df['documento'] = df['documento'].astype(str)

logging.info("Inicia busqueda de documento en tablas internas")
df['Clasificación'] = 'No se encontró en BD'
#Hacemos la busqueda del campo "documento" de la fuente en las dos tablas y clasificamos el nuevo campo Clasificacion
df.loc[df['documento'].isin(df_sqlite_clientes['documento']), 'Clasificación'] = 'Cartera de Clientes' 

#Dejamos por ultimo lista de control, para que le de prioridad y sea el ultimo valor que almacene el DataFrame final.
df.loc[df['documento'].isin(df_sqlite_control['documento']), 'Clasificación'] = 'Lista de control'

registrar_proceso(conn, 500001, 'Finaliza del Proceso de cruce de datos', 'Finalizado')

#Parametrizamos la fecha y hora en formato YYYYMMDD_HHMISS para customizar el nombre del archivo generado en base a una fecha.
fecha_hora_actual = datetime.now().strftime('%Y%m%d_%H%M%S')

logging.info(f"Se generaron {df.count()} registros en total")

logging.info(f"Guardando archivo Excel:resultado_{fecha_hora_actual}")

#Generamos nuevo archivo 
df.to_excel(f'C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/resultado_{fecha_hora_actual}.xlsx', index=False)



registrar_proceso(conn, 500001, 'Finaliza el Proceso Carga Clientes', 'Finalizado')