import pandas as pd
import streamlit as st
import pip
import datetime
import pytz
from PIL import Image

image = Image.open("./images/logo1.png")
st.sidebar.image(image,width=150,use_column_width=False)
image1 = Image.open("./images/Partes-Criticas.jpg")
st.image(image1, caption=None, width=750, use_column_width=None, clamp=False, channels="RGB", output_format="auto")




# Obtener la fecha y hora actual en UTC
fecha_hora_actual_utc = datetime.datetime.now(pytz.utc)

# Convertir la fecha y hora actual a la zona horaria de Argentina (GMT-3)
zona_horaria_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
fecha_hora_actual_argentina = fecha_hora_actual_utc.astimezone(zona_horaria_argentina)

# Formatear la fecha y hora en un formato específico
fecha_hora_formateada = fecha_hora_actual_argentina.strftime("%d-%m-%Y")

# Mostrar la fecha y hora de la última actualización en la barra lateral
st.sidebar.write(f"Última actualización: {fecha_hora_formateada}")




st.markdown ('**TOP PARTES**')
pip.main(["install","openpyxl"])

df = pd.read_excel("intento70-30.xlsx")

pdescripciones=pd.read_excel("FormatoNsPartes.xlsx")

daily = pd.read_excel("Daily.xlsx")

# Combinar los dataframes en función de la columna "PARTES" y "PARTE"
merged_df = pd.merge(df, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')

# Renombrar la columna 'DESCRIPCION' a 'descripciones'
merged_df.rename(columns={'DESCRIPCION': 'descripciones'}, inplace=True)

# Eliminar la columna 'PARTE' redundante
merged_df.drop(columns=['PARTE'], inplace=True)

# Agrupar por número de parte y contar tickets únicos
tickets_por_parte = df.groupby('PARTES')['TICKET NUMBER'].nunique().reset_index()

# Renombrar la columna 'TICKET NUMBER' a 'TICKETS AFECTADOS'
tickets_por_parte.rename(columns={'TICKET NUMBER': 'TICKETS AFECTADOS'}, inplace=True)

# Fusionar con pdescripciones para obtener descripciones
tickets_por_parte = pd.merge(tickets_por_parte, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')

# Filtrar registros con más de 10 tickets afectados
resultado_final = tickets_por_parte[tickets_por_parte['TICKETS AFECTADOS'] >= 10]

# Ordenar los resultados de mayor a menor según el número de tickets afectados
resultado_final = resultado_final.sort_values(by='TICKETS AFECTADOS', ascending=False)

# Seleccionar las columnas requeridas y cambiar el orden
resultado_final = resultado_final[['PARTES', 'DESCRIPCION', 'TICKETS AFECTADOS']]

# Ordenar los resultados de mayor a menor según el número de tickets afectados
resultado_final = resultado_final.sort_values(by='TICKETS AFECTADOS', ascending=False)
# Mostrar el resultado

st.table(resultado_final)

st.markdown ('**SOLICITUDES**')
# Filtrar las columnas deseadas
columnas_deseadas = ['ESTATUS', 'VENDOR', 'ITEM', 'DESCRIPTION', 'QTY', 'REAL SHIPPING DATE', 'CUSTOMS ARRIVAL', 'ETA WAREHOUSE', 'REAL DELIVERY DATE']
resultado_filtrado = daily[columnas_deseadas]

# Crear el menú desplegable para seleccionar una parte específica
parte_seleccionada = st.selectbox("Selecciona una parte:", [""] + resultado_final['PARTES'].tolist())

# Filtrar los resultados según la parte seleccionada
if parte_seleccionada:
    resultado_filtrado = resultado_filtrado[resultado_filtrado['ITEM'] == parte_seleccionada]
    st.write("Información para la parte seleccionada:")
    st.table(resultado_filtrado)
else:
    st.write("Por favor, selecciona una parte para ver la información.")
