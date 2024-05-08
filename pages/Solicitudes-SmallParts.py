import pandas as pd
import streamlit as st
import pip
import datetime
import pytz

# Obtener la fecha y hora actual en UTC
fecha_hora_actual_utc = datetime.datetime.now(pytz.utc)

# Convertir la fecha y hora actual a la zona horaria de Argentina (GMT-3)
zona_horaria_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
fecha_hora_actual_argentina = fecha_hora_actual_utc.astimezone(zona_horaria_argentina)

# Formatear la fecha y hora en un formato específico
fecha_hora_formateada = fecha_hora_actual_argentina.strftime("%Y-%m-%d %H:%M:%S")

# Mostrar la fecha y hora de la última actualización en la barra lateral
st.sidebar.write(f"Última actualización: {fecha_hora_formateada}")



pip.main(["install", "openpyxl"])

# Cargar los DataFrames
df = pd.read_excel("./intento70-30.xlsx")
pdescripciones = pd.read_excel("./FormatoNsPartes.xlsx")
bom = pd.read_excel("./BOM.xlsx")
daily = pd.read_excel("./Daily.xlsx")

# Combinar los dataframes en función de la columna "PARTES" y "PARTE"
merged_df = pd.merge(df, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')
merged_df.rename(columns={'DESCRIPCION': 'descripciones'}, inplace=True)
merged_df.drop(columns=['PARTE'], inplace=True)

# Agrupar por número de parte y contar tickets únicos
tickets_por_parte = df.groupby('PARTES')['TICKET NUMBER'].nunique().reset_index()
tickets_por_parte.rename(columns={'TICKET NUMBER': 'TICKETS AFECTADOS'}, inplace=True)
tickets_por_parte = pd.merge(tickets_por_parte, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')
resultado_final = tickets_por_parte[tickets_por_parte['TICKETS AFECTADOS'] >= 10]
resultado_final = resultado_final[['PARTES', 'DESCRIPCION', 'TICKETS AFECTADOS']]
resultado_final = resultado_final.sort_values(by='TICKETS AFECTADOS', ascending=False)

# Mostrar el resultado en Streamlit
st.markdown('PARTES SOLICITADAS')
st.table(resultado_final)

# Filtrar el DataFrame "bom" para incluir solo los elementos con más de 10 tickets afectados
bom_filtrado = bom[bom['Item'].isin(resultado_final['PARTES'])]

# Obtener los elementos únicos de la columna "Item" para el selectbox
items_seleccionables = bom_filtrado['Item'].unique()

# Componente de selección de usuario para elegir un ítem
selected_item = st.selectbox("Seleccione un ítem:", items_seleccionables)

# Filtrar el DataFrame "bom" según el ítem seleccionado por el usuario
if selected_item:
    filtered_bom = bom[bom['Item'] == selected_item][['Item', 'Item Refaccion', 'Descripción Refaccion']]
    st.markdown('Tabla de BOM filtrada por el ítem seleccionado:')
    st.table(filtered_bom)
    
    # Obtener los ítems de refacción únicos para el ítem seleccionado
    refacciones_seleccionadas = filtered_bom['Item Refaccion'].unique()
    
    # Filtrar el DataFrame "daily" y sumar la cantidad de cada ítem refacción
    if refacciones_seleccionadas.any():
        filtered_daily = daily[daily['ITEM'].isin(refacciones_seleccionadas)]
        cantidad_refacciones = filtered_daily.groupby('ITEM').agg({'QTY':'sum', 'ESTATUS':'first'}).reset_index()
        st.markdown('Cantidad total y estado de cada ítem refacción en el Daily:')
        st.table(cantidad_refacciones)
    else:
        st.write("No hay ítems de refacción asociados a este ítem seleccionado.")
        # Crear un DataFrame con los ítems de refacción sin solicitud
    refacciones_sin_solicitud = pd.DataFrame(columns=['Item Refaccion', 'Estado'])
    refacciones_sin_solicitud['Item Refaccion'] = filtered_bom[~filtered_bom['Item Refaccion'].isin(filtered_daily['ITEM'])]['Item Refaccion']
    refacciones_sin_solicitud['Estado'] = 'Sin solicitud'
    
    # Mostrar la tabla con los ítems de refacción sin solicitud
    st.markdown('Ítems de refacción sin solicitud asociada:')
    st.table(refacciones_sin_solicitud)


