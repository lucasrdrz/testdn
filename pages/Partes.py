import pandas as pd
import streamlit as st
import base64
import datetime
import pytz
from PIL import Image

image = Image.open("./images/logo1.png")
st.sidebar.image(image,width=150,use_column_width=False)
# Obtener la fecha y hora actual en UTC
fecha_hora_actual_utc = datetime.datetime.now(pytz.utc)

# Convertir la fecha y hora actual a la zona horaria de Argentina (GMT-3)
zona_horaria_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
fecha_hora_actual_argentina = fecha_hora_actual_utc.astimezone(zona_horaria_argentina)

# Formatear la fecha y hora en un formato específico
fecha_hora_formateada = fecha_hora_actual_argentina.strftime("%d-%m-%Y")

# Mostrar la fecha y hora de la última actualización en la barra lateral
st.sidebar.write(f"Última actualización: {fecha_hora_formateada}")




# Cargar los dataframes

merged_df = pd.read_excel("intento70-30.xlsx")

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
    numeros_parte_cliente = cliente_seleccionado_df.groupby('PARTES').agg({'TICKET NUMBER': ['nunique', list], 'descripciones': 'first'}).reset_index()
    
    # Renombrar las columnas
    numeros_parte_cliente.columns = ['PARTES', 'TICKETS AFECTADOS', 'LISTA TICKETS', 'DESCRIPCION']
    
    # Ordenar los resultados de mayor a menor según el total de tickets afectados
    numeros_parte_cliente = numeros_parte_cliente.sort_values(by='TICKETS AFECTADOS', ascending=False)

    # Agregar el número de ticket al principio de cada fila
    numeros_parte_cliente['LISTA TICKETS'] = numeros_parte_cliente.apply(lambda row: ', '.join(map(str, row['LISTA TICKETS'])), axis=1)

    # Reordenar las columnas
    numeros_parte_cliente = numeros_parte_cliente[['LISTA TICKETS', 'PARTES', 'DESCRIPCION', 'TICKETS AFECTADOS']]

    # Desplegable para mostrar los tickets individualmente
    show_tickets = st.checkbox("Mostrar tickets")
    if show_tickets:
        st.table(numeros_parte_cliente)
    else:
        st.table(numeros_parte_cliente[['PARTES', 'DESCRIPCION', 'TICKETS AFECTADOS']])

    # Exportar los resultados a un archivo CSV si se hace clic en un botón
    if st.button("Exportar a CSV"):
        csv = numeros_parte_cliente.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="resultados_cliente_seleccionado.csv">Descargar archivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.write("No se encontraron datos para el cliente seleccionado.")
    
