import pandas as pd
import streamlit as st
import datetime
import pytz
from PIL import Image

image = Image.open("./images/logo1.png")
st.sidebar.image(image,width=150,use_column_width=False)
image1 = Image.open("./images/Solicitudes-Clientes.jpg")
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


st.markdown('En esta pantalla podemos filtrar por Numero de parte y ver como impacta en los clientes.')



df = pd.read_excel("intento70-30.xlsx")

pdescripciones=pd.read_excel("FormatoNsPartes.xlsx")

# Combinar los dataframes en función de la columna "PARTES" y "PARTE"
merged_df = pd.merge(df, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')

# Renombrar la columna 'DESCRIPCION' a 'descripciones'
merged_df.rename(columns={'DESCRIPCION': 'descripciones'}, inplace=True)

# Eliminar la columna 'PARTE' redundante
merged_df.drop(columns=['PARTE'], inplace=True)

# Guardar el resultado si es necesario
# merged_df.to_excel('resultado.xlsx', index=False)

# Agrupar por número de parte y contar tickets únicos
tickets_por_parte = df.groupby('PARTES')['TICKET NUMBER'].nunique().reset_index()

# Renombrar la columna 'TICKET NUMBER' a 'TICKETS AFECTADOS'
tickets_por_parte.rename(columns={'TICKET NUMBER': 'TICKETS AFECTADOS'}, inplace=True)

# Fusionar con pdescripciones para obtener descripciones
tickets_por_parte = pd.merge(tickets_por_parte, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')

# Seleccionar las columnas requeridas
resultado_final = tickets_por_parte[['PARTES', 'DESCRIPCION', 'TICKETS AFECTADOS']]

# Ordenar los resultados de mayor a menor según el número de tickets afectados
resultado_final = resultado_final.sort_values(by='TICKETS AFECTADOS', ascending=False)

st.markdown('CLIENTES AFECTADOS POR PARTE')

# Obtener el número de parte específica ingresado por el usuario
parte_especifica = st.selectbox("Selecciona una parte:", [""] + resultado_final['PARTES'].tolist())

# Filtrar el DataFrame por la parte específica ingresada
parte_especifica_df = merged_df[merged_df['PARTES'] == parte_especifica]

# Verificar si hay datos para el número de parte ingresado
if not parte_especifica_df.empty:
    # Contar la cantidad de veces que aparece cada cliente afectado
    clientes_afectados = parte_especifica_df.groupby('NOMBRE CLIENTE').size().reset_index(name='TOTAL')
    
    # Ordenar los resultados de mayor a menor según la cantidad total de ocurrencias
    clientes_afectados = clientes_afectados.sort_values(by='TOTAL', ascending=False)
    
    # Calcular la suma total
    total_sum = clientes_afectados['TOTAL'].sum()
    
    # Agregar la fila del total al final del DataFrame
    total_row = pd.DataFrame({'NOMBRE CLIENTE': ['Total'], 'TOTAL': [total_sum]})
    clientes_afectados = pd.concat([clientes_afectados, total_row], ignore_index=True)

    # Mostrar los resultados
    st.table(clientes_afectados)
else:
    st.write("No se encontraron datos para el número de parte especificado.")
