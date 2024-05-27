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

# Verificar las columnas en los DataFrames
#st.write("Columnas en df:", df.columns.tolist())
#st.write("Columnas en reporte_reparacion_min:", reporte_reparacion_min.columns.tolist())

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

# Crear una columna que contenga todas las partes asociadas con el mismo ticket, sin duplicados
merged_df['OTRAS PARTES'] = merged_df.groupby('TICKET NUMBER')['PARTES'].transform(lambda x: ', '.join(sorted(set(x))))

# Combinar los datos para mostrar la parte específica y las otras partes
parte_especifica = st.selectbox("Selecciona una parte:", [""] + merged_df['PARTES'].unique().tolist())
parte_especifica_df = merged_df[merged_df['PARTES'] == parte_especifica]

# Verificar si hay datos para la parte específica ingresada
if not parte_especifica_df.empty:
    # Eliminar la parte específica de la columna 'OTRAS PARTES'
    parte_especifica_df['OTRAS PARTES'] = parte_especifica_df.apply(
        lambda row: ', '.join([p for p in row['OTRAS PARTES'].split(', ') if p != parte_especifica]),
        axis=1
    )
    
    # Seleccionar las columnas requeridas y eliminar duplicados
    clientes_afectados = parte_especifica_df[['TICKET NUMBER', 'FECHA GENERACION TICKET', 'NOMBRE CLIENTE', 'PARTES', 'OTRAS PARTES']].drop_duplicates()
    
    # Contar la cantidad de veces que aparece cada cliente afectado
    clientes_totales = clientes_afectados.groupby('NOMBRE CLIENTE').size().reset_index(name='TOTAL')
    
    # Ordenar los resultados de mayor a menor según la cantidad total de ocurrencias
    clientes_totales = clientes_totales.sort_values(by='TOTAL', ascending=False)
    
    # Calcular la suma total
    total_sum = clientes_totales['TOTAL'].sum()
    
    # Agregar la fila del total al final del DataFrame
    total_row = pd.DataFrame({'NOMBRE CLIENTE': ['Total'], 'TOTAL': [total_sum]})
    clientes_totales = pd.concat([clientes_totales, total_row], ignore_index=True)

    # Mostrar los resultados
    st.table(clientes_totales)
    
    # Mostrar los detalles de los tickets
    st.table(clientes_afectados)
else:
    st.write("No se encontraron datos para el número de parte especificado.")



