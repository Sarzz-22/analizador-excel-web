import streamlit as st
import pandas as pd
import os

# =======================================================
# 1. CONFIGURACIÓN DE COLUMNAS (¡IGUAL QUE ANTES!)
# =======================================================

COLUMNA_INICIADOR = 'Iniciador' 
COLUMNA_DEPOSITAR = 'Depositar' 

# =======================================================
# 2. FUNCIÓN DE PROCESAMIENTO
# Recibe el archivo subido por el usuario
# =======================================================

def procesar_datos_excel(archivo_cargado):
    """Realiza la lógica de filtrado y suma."""
    try:
        # Pandas detecta automáticamente el formato (xls o xlsx)
        # cuando recibe un objeto de archivo cargado.
        df = pd.read_excel(archivo_cargado, engine='openpyxl') 
    except Exception as e:
        st.error(f"❌ ERROR al leer el archivo. Asegúrate de que sea un archivo .xlsx o .xls válido. Detalles: {e}")
        return None, None

    # Verificar que las columnas existan
    if COLUMNA_INICIADOR not in df.columns or COLUMNA_DEPOSITAR not in df.columns:
        st.error(f"❌ ERROR: Las columnas requeridas ('{COLUMNA_INICIADOR}', '{COLUMNA_DEPOSITAR}') no fueron encontradas.")
        st.write("Columnas disponibles:", list(df.columns))
        return None, None

    # --- FILTRADO: Buscar números que terminan en .01 ---
    
    df[COLUMNA_DEPOSITAR] = pd.to_numeric(df[COLUMNA_DEPOSITAR], errors='coerce')
    df_limpio = df.dropna(subset=[COLUMNA_DEPOSITAR])

    df_filtrado = df_limpio[
        (df_limpio[COLUMNA_DEPOSITAR] * 100).round(0) % 100 == 1
    ].copy()
    
    # --- AGRUPACIÓN Y SUMA POR INICIADOR ---
    
    resultados_por_iniciador = df_filtrado.groupby(COLUMNA_INICIADOR)[COLUMNA_DEPOSITAR].sum().reset_index()
    
    return resultados_por_iniciador

# =======================================================
# 3. INTERFAZ DE STREAMLIT (ASPECTO VISUAL)
# =======================================================

st.set_page_config(page_title="Analizador de Depósitos .01", layout="centered")

st.title("📊 Analizador Web de Depósitos de Iniciadores")
st.markdown("---")

st.subheader("1. Cargar Archivo de Excel (.xlsx o .xls)")

# Widget para que el usuario suba el archivo
archivo_cargado = st.file_uploader(
    "Sube aquí tu archivo de Excel con las columnas 'Iniciador' y 'Depositar'.", 
    type=['xlsx', 'xls']
)

# Instrucciones visuales
st.info(f"El sistema buscará las columnas llamadas **'{COLUMNA_INICIADOR}'** y **'{COLUMNA_DEPOSITAR}'** y filtrará las entradas que terminan en **.01**.")

if archivo_cargado:
    st.subheader("2. Resultados del Análisis")
    
    # Llamar a la función de procesamiento
    resultados = procesar_datos_excel(archivo_cargado)
    
    if resultados is not None:
        
        # Calcular la suma total
        suma_total_final = resultados[COLUMNA_DEPOSITAR].sum()
        
        # Mostrar el resultado total en una métrica grande
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Total de Iniciadores Únicos", 
                value=len(resultados)
            )
        with col2:
            st.metric(
                label="⭐ SUMA TOTAL FINAL de Depósitos .01", 
                value=f"{suma_total_final:,.2f} USD"
            )

        st.markdown("---")
        
        st.subheader("Desglose por Iniciador")
        
        # Renombrar la columna para mejor presentación
        resultados.columns = ['Iniciador', 'Suma Total Depósitos .01']
        
        # Mostrar los resultados en una tabla interactiva
        st.dataframe(
            resultados, 
            hide_index=True, 
            use_container_width=True
        )