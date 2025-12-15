import streamlit as st
import pandas as pd
import os


COLUMNA_INICIADOR = 'Iniciador' 
COLUMNA_DEPOSITAR = 'Depositar' 

@st.cache_data(show_spinner=False)
def procesar_datos_excel(archivo_cargado):
    """
    Realiza la lógica de filtrado y suma.
    Detecta la extensión para usar el motor de Pandas correcto (.xls -> xlrd, .xlsx -> openpyxl).
    """
    
    
    nombre_archivo = archivo_cargado.name.lower()
    motor_lectura = 'openpyxl'
    
    if nombre_archivo.endswith('.xls'):
        motor_lectura = 'xlrd'

    
    try:

        df = pd.read_excel(archivo_cargado, engine=motor_lectura) 
        
    except Exception as e:
      
        st.error(f"❌ ERROR al leer el archivo. Asegúrate de que sea un archivo .xlsx o .xls válido.")
        st.caption(f"Detalles técnicos (para depuración): {e}")
        return None


    
    if COLUMNA_INICIADOR not in df.columns or COLUMNA_DEPOSITAR not in df.columns:
        st.error(f"❌ ERROR: Las columnas requeridas ('{COLUMNA_INICIADOR}', '{COLUMNA_DEPOSITAR}') no fueron encontradas.")
        st.write("Columnas disponibles en el archivo:", list(df.columns))
        return None

   
    
   
    df[COLUMNA_DEPOSITAR] = pd.to_numeric(df[COLUMNA_DEPOSITAR], errors='coerce')
    df_limpio = df.dropna(subset=[COLUMNA_DEPOSITAR])

  
    df_filtrado = df_limpio[
        (df_limpio[COLUMNA_DEPOSITAR] * 100).round(0) % 100 == 1
    ].copy()
    
    
    
    resultados_por_iniciador = df_filtrado.groupby(COLUMNA_INICIADOR)[COLUMNA_DEPOSITAR].sum().reset_index()
    
    return resultados_por_iniciador



st.set_page_config(page_title="Analizador de Depósitos .01", layout="centered")

st.title("📊 Analizador Web de Depósitos de Iniciadores")
st.markdown("---")

st.subheader("1. Cargar Archivo de Excel")


archivo_cargado = st.file_uploader(
    "Sube aquí tu archivo de Excel. Se acepta formato .xlsx (moderno) o .xls (antiguo).", 
    type=['xlsx', 'xls']
)


st.info(f"El sistema buscará las columnas llamadas **'{COLUMNA_INICIADOR}'** y **'{COLUMNA_DEPOSITAR}'** y filtrará las entradas que terminan en **.01** para sumarlas.")

if archivo_cargado:
    st.subheader("2. Resultados del Análisis")
    
  
    with st.spinner('Analizando datos y aplicando filtros...'):
        resultados = procesar_datos_excel(archivo_cargado)
    
    if resultados is not None and not resultados.empty:
        
     
        suma_total_final = resultados[COLUMNA_DEPOSITAR].sum()
        
     
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Total de Iniciadores Únicos", 
                value=len(resultados)
            )
        with col2:
            st.metric(
                label="⭐ SUMA TOTAL FINAL de Depósitos .01", 
                value=f"{suma_total_final:,.2f}"
            )

        st.markdown("---")
        
        st.subheader("Desglose por Iniciador")
        
     
        resultados.columns = ['Iniciador', 'Suma Total Depósitos .01']
        
       
        st.dataframe(
            resultados, 
            hide_index=True, 
            use_container_width=True
        )
        
    elif resultados is not None and resultados.empty:
        st.warning("⚠️ El archivo se leyó correctamente, pero no se encontraron depósitos que terminaran en .01 con los nombres de columna especificados.")
        st.dataframe(
            resultados, 
            hide_index=True, 
            use_container_width=True

        )

