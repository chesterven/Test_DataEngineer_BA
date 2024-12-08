import pandas as pd 
import re
from datetime import datetime
import sqlite3


# Inicializamos el dataframe con el archivo fuente
df = pd.read_excel('C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/fuente.xlsx') 



#Creamos metodo para limpiar los datos del nombre y DUI. 
def stage_limpieza(texto):
    # Eliminar caracteres especiales y números
    texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóú\s]', '', texto)
    
    # Reemplazar múltiples espacios en blanco por uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    return texto_limpio


#Creamos metodo para la clasificacion del nombre.
def clasificar_nombre_cliente(nombre_completo):
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


# Invocacion de funcion de clasificacion de nombres
df[['Nombre1', 'Nombre2', 'Nombre3', 'Apellido1', 'Apellido2', 'Casada']] = df['Nombre'].apply(clasificar_nombre_cliente)

#Eliminamos la primera columna
df = df.iloc[:, 1:]

#Nos coenctamos a la base de datos ClientesListasBA que fue proporcionada para la prueba
conn = sqlite3.connect('C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/ClientesListasBA.db')

#Ejecutamos consultas sin filtros para obtener todos los registros de las tablas internas.
df_sqlite_clientes = pd.read_sql_query('SELECT * FROM clientes', conn)
df_sqlite_control = pd.read_sql_query('SELECT * FROM lista_control', conn)

#Parametrizando el campo documento a tipo texto previo al cruce
df['documento'] = df['documento'].astype(str)


#Hacemos la busqueda del campo "documento" de la fuente en las dos tablas y clasificamos el nuevo campo Clasificacion
df.loc[df['documento'].isin(df_sqlite_clientes['documento']), 'Clasificación'] = 'Cartera de Clientes' 

#Dejamos por ultimo lista de control, para que le de prioridad y sea el ultimo valor que almacene el DataFrame final.
df.loc[df['documento'].isin(df_sqlite_control['documento']), 'Clasificación'] = 'Lista de control'

#Parametrizamos la fecha y hora en formato YYYYMMDD_HHMISS para customizar el nombre del archivo generado en base a una fecha.
fecha_hora_actual = datetime.now().strftime('%Y%m%d_%H%M%S')



#Generamos nuevo archivo 
df.to_excel(f'C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/resultado_{fecha_hora_actual}.xlsx', index=False)
