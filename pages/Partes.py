import pandas as pd
import streamlit as st
import base64

# Cargar los dataframes

merged_df = pd.read_excel("intento70-30-05-04.xlsx")

pdescripciones=pd.read_excel("FormatoNsPartes.xlsx")

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
    # Agrupar por número de parte y contar la cantidad de ocurrencias para el cliente seleccionado
    numeros_parte_cliente = cliente_seleccionado_df.groupby('PARTES').agg({'TICKET NUMBER': 'nunique', 'descripciones': 'first'}).reset_index()
    
    # Renombrar las columnas
    numeros_parte_cliente.rename(columns={'TICKET NUMBER': 'TICKETS AFECTADOS', 'descripciones': 'DESCRIPCION'}, inplace=True)
    
    # Ordenar los resultados de mayor a menor según el total de tickets afectados
    numeros_parte_cliente = numeros_parte_cliente.sort_values(by='TICKETS AFECTADOS', ascending=False)

    # Mostrar los resultados
    st.table(numeros_parte_cliente)

    # Exportar los resultados a un archivo CSV si se hace clic en un botón
    if st.button("Exportar a CSV"):
        csv = numeros_parte_cliente.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="resultados_cliente_seleccionado.csv">Descargar archivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.write("No se encontraron datos para el cliente seleccionado.")

    
