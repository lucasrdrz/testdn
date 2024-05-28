import pandas as pd
import streamlit as st
import base64
from PIL import Image

image = Image.open("./images/logo1.png")
st.sidebar.image(image,width=150,use_column_width=False)
# Cargar los dataframes
merged_df = pd.read_excel("./intento70-30.xlsx")
pdescripciones = pd.read_excel("./FormatoNsPartes.xlsx")

# Combinar los dataframes en función de la columna "PARTES" y "PARTE"
merged_df = pd.merge(merged_df, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')

# Renombrar la columna 'DESCRIPCION' a 'descripciones'
merged_df.rename(columns={'DESCRIPCION': 'descripciones'}, inplace=True)

# Eliminar la columna 'PARTE' redundante
merged_df.drop(columns=['PARTE'], inplace=True)

# Obtener la lista de clientes únicos
clientes_unicos = merged_df['NOMBRE CLIENTE'].unique()

# Permitir al usuario seleccionar el cliente mediante un select box
cliente_seleccionado = st.selectbox("Seleccione el cliente:", clientes_unicos)

# Filtrar el DataFrame por el cliente seleccionado
cliente_seleccionado_df = merged_df[merged_df['NOMBRE CLIENTE'] == cliente_seleccionado]

# Verificar si hay datos para el cliente seleccionado
if not cliente_seleccionado_df.empty:
    # Seleccionar las columnas necesarias
    resultados_cliente = cliente_seleccionado_df[['TICKET NUMBER', 'descripciones', 'PARTES']]
    
    # Mostrar los resultados
    st.table(resultados_cliente)

    # Exportar los resultados a un archivo CSV si se hace clic en un botón
    if st.button("Exportar a CSV"):
        csv = resultados_cliente.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="resultados_cliente_seleccionado.csv">Descargar archivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.write("No se encontraron datos para el cliente seleccionado.")
