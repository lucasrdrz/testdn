import pandas as pd
import streamlit as st
import datetime
import pytz

# Obtener la fecha y hora actual en UTC
fecha_hora_actual_utc = datetime.datetime.now(pytz.utc)

# Convertir la fecha y hora actual a la zona horaria de Argentina (GMT-3)
zona_horaria_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
fecha_hora_actual_argentina = fecha_hora_actual_utc.astimezone(zona_horaria_argentina)

# Formatear la fecha y hora en un formato específico
fecha_hora_formateada = fecha_hora_actual_argentina.strftime("%d-%m-%Y")

# Mostrar la fecha y hora de la última actualización en la barra lateral
st.sidebar.write(f"Última actualización: {fecha_hora_formateada}")

# Cargar los archivos Excel
df = pd.read_excel("./intento70-30.xlsx")
pdescripciones = pd.read_excel("./FormatoNsPartes.xlsx")
reporte_reparacion = pd.read_excel("./ReporteReparacionEfectiveOnline.xlsx")

# Crear una tabla mínima de reporte_reparacion con 'TICKET NUMBER' y 'FECHA GENERACION TICKET'
reporte_reparacion_min = reporte_reparacion[['TICKET NUMBER', 'FECHA GENERACION TICKET']]

# Combinar los dataframes en función de la columna "PARTES" y "PARTE"
merged_df = pd.merge(df, pdescripciones[['PARTE', 'DESCRIPCION']], how='left', left_on='PARTES', right_on='PARTE')

# Renombrar la columna 'DESCRIPCION' a 'descripciones'
merged_df.rename(columns={'DESCRIPCION': 'descripciones'}, inplace=True)

# Eliminar la columna 'PARTE' redundante
merged_df.drop(columns=['PARTE'], inplace=True)

# Unir merged_df con reporte_reparacion_min en función de 'TICKET NUMBER'
merged_df = pd.merge(merged_df, reporte_reparacion_min, on='TICKET NUMBER', how='left')

# Convertir la columna 'PARTES' a cadena de texto
merged_df['PARTES'] = merged_df['PARTES'].astype(str)

# Crear una columna que contenga todas las partes asociadas con el mismo ticket, sin duplicados en PARTES y OTRAS PARTES
merged_df['OTRAS PARTES'] = merged_df.groupby('TICKET NUMBER')['PARTES'].transform(lambda x: ', '.join(sorted(set(x))))

# Eliminar partes duplicadas entre PARTES y OTRAS PARTES
def eliminar_duplicados(row):
    partes = set(row['PARTES'].split(', '))
    otras_partes = set(row['OTRAS PARTES'].split(', '))
    otras_partes = otras_partes - partes
    return ', '.join(otras_partes)

merged_df['OTRAS PARTES'] = merged_df.apply(eliminar_duplicados, axis=1)

# Cargar el archivo de stock que suba el usuario
st.sidebar.write("Sube tu archivo de stock:")
stock_file = st.sidebar.file_uploader("Selecciona el archivo de stock en formato Excel", type=["xlsx"])
if stock_file:
    stock_df = pd.read_excel(stock_file)
    stock_df['PARTES'] = stock_df['PARTES'].astype(str)
else:
    st.write("Por favor, sube un archivo de stock para realizar la comparación.")

# Opción de filtrado
filtro_opcion = st.selectbox("Selecciona una opción de filtrado:", ["Por cliente", "Mostrar todo"])

# Filtrado por cliente o mostrar todo
if filtro_opcion == "Por cliente":
    cliente = st.selectbox("Selecciona un cliente:", [""] + merged_df['NOMBRE CLIENTE'].unique().tolist())
    if cliente:
        filtrado_df = merged_df[merged_df['NOMBRE CLIENTE'] == cliente]
    else:
        filtrado_df = pd.DataFrame()
        st.write("Por favor, selecciona un cliente válido.")
elif filtro_opcion == "Mostrar todo":
    filtrado_df = merged_df.copy()

# Comparación entre las partes necesarias y el stock disponible
if stock_file and not filtrado_df.empty:
    def verificar_stock(row):
        partes_necesarias = row['PARTES'].split(', ')
        if row['OTRAS PARTES']:
            partes_necesarias += row['OTRAS PARTES'].split(', ')
        status = []
        
        for parte in partes_necesarias:
            if parte:
                stock_info = stock_df[stock_df['PARTES'] == parte]
                if not stock_info.empty:
                    cantidad_disponible = stock_info['stock'].values[0]
                    status.append(f"{parte}: Ok ({cantidad_disponible} disponibles)")
                else:
                    status.append(f"{parte}: Falta")
        
        return "; ".join(status)
    
    filtrado_df['STATUS'] = filtrado_df.apply(verificar_stock, axis=1)

# Eliminar duplicados por 'TICKET NUMBER'
filtrado_df = filtrado_df.drop_duplicates(subset='TICKET NUMBER')

# Mostrar los resultados según el filtro aplicado
if not filtrado_df.empty:
    st.table(filtrado_df[['TICKET NUMBER', 'FECHA GENERACION TICKET', 'NOMBRE CLIENTE', 'PARTES', 'OTRAS PARTES', 'STATUS']])
else:
    st.write("No se encontraron datos según los filtros aplicados.")
