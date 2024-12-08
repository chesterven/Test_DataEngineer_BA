import pandas as pd
import requests
from lxml import etree
import urllib.request

# URL ONU
url = 'https://scsanctions.un.org/resources/xml/en/consolidated.xml'

# Enviar request y obtener el response xml
response = urllib.request.urlopen(url)
xml_data = etree.parse(response)

# Parsear el contenido XML
root = xml_data.getroot()


# Función para convertir el XML en un DataFrame
def xml_to_dataframe(root):
    all_records = [] 
     
    for child in root.findall('.//INDIVIDUAL'): 
            for element in child: 
                record_data = {}
                record_data[element.tag] = element.text 
            all_records.append(record_data)
    return pd.DataFrame(all_records)

# Crear el DataFrame
df = xml_to_dataframe(root)

# Mostrar las primeras filas del DataFrame
print(df.head(), df.count)

df.to_excel(f'C:/Users/chest/OneDrive/Escritorio/Prueba técnica BA/evaluación_ing_datos/evaluación_externa/ONU.xlsx', index=False)
