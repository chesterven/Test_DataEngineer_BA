import pandas as pd 
import re
from datetime import datetime
import sqlite3
# Leer el archivo Excel 


df = pd.read_excel('C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/fuente.xlsx') 
# Mostrar las primeras filas del DataFrame 
print(df.head())

#Limpiamos la data

def stage_limpieza(texto):
    # Eliminar caracteres especiales y números
    texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóú\s]', '', texto)
    
    # Reemplazar múltiples espacios en blanco por uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    return texto_limpio



def clasificar_nombre_cliente(nombre_completo):
    # Dividir el nombre completo en partes
    nombre_clean = stage_limpieza(nombre_completo)

    

    partes = re.split(r'\s+', nombre_clean.strip())
    
    #print(partes)

    nombre1, nombre2, nombre3 = '', '', ''
    apellido1, apellido2, casada = '', '', ''
    
    
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
df = df.iloc[:, 1:]

conn = sqlite3.connect('C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/ClientesListasBA.db')


df_sqlite_clientes = pd.read_sql_query('SELECT * FROM clientes', conn)

#Parametrizando el campo documento a tipo texto previo al cruce
df['documento'] = df['documento'].astype(str)

df_clientes = pd.merge(df, df_sqlite_clientes, on='documento', how='inner', indicator=True) 

df['Clasificación'] = df_clientes['_merge'].apply(lambda x: 'Clientes' if x == 'both' else 'No encontrado se encontro en BD')
# Mostrar el resultado del cruce 

df_sqlite_control = pd.read_sql_query('SELECT * FROM lista_control', conn)

#Parametrizando el campo documento a tipo texto previo al cruce

df_control = pd.merge(df, df_sqlite_control, on='documento', how='inner', indicator=True) 

df['Clasificación'] = df_control['_merge'].apply(lambda x: 'Lista de Control' if x == 'both' else 'No encontrado se encontro en BD')


fecha_hora_actual = datetime.now().strftime('%Y%m%d_%H%M%S')



#Generamos nuevo archivo 
df.to_excel(f'C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/resultado_{fecha_hora_actual}.xlsx', index=False)

# Mostrar las primeras filas del DataFrame con las nuevas columnas
#print(df.head())
