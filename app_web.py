import streamlit as st
import pandas as pd
import os

# =======================================================
# 1. CONFIGURACIÓN DE COLUMNAS (Basado en tu imagen)
# =======================================================

# Usamos los nombres exactos que aparecen en tu Excel
COLUMNA_INICIADOR = 'Iniciador' 
COLUMNA_DEPOSITAR = 'Depositar' 

# =======================================================
# 2. FUNCIÓN DE PROCESAMIENTO (Con detección de formato)
# =======================================================

@st.cache_data(show_spinner=False)
def procesar_datos_excel(archivo_cargado):
    """
    Realiza la lógica de filtrado y suma.
    Detecta la extensión para usar el motor de Pandas correcto (.xls -> xlrd, .xlsx -> openpyxl).
    """
    
    # --- Detección de la extensión para elegir el motor ---
    
    nombre_archivo = archivo_cargado.name.lower()
    motor_lectura = 'openpyxl' # Valor predeterminado para .xlsx
    
    if nombre_archivo.endswith('.xls'):
        # Si termina en .xls, usamos el motor xlrd
        motor_lectura = 'xlrd'
    
    # ----------------------------------------------------
    
    try:
        # Usamos el motor detectado
        df = pd.read_excel(archivo_cargado, engine=motor_lectura) 
        
    except Exception as e:
        # st.error muestra el error en la web app
        st.error(f"❌ ERROR al leer el archivo. Asegúrate de que sea un archivo .xlsx o .xls válido.")
        st.caption(f"Detalles técnicos (para depuración): {e}")
        return None

    # --- Verificación de Columnas ---
    
    if COLUMNA_INICIADOR not in df.columns or COLUMNA_DEPOSITAR not in df.columns:
        st.error(f"❌ ERROR: Las columnas requeridas ('{COLUMNA_INICIADOR}', '{COLUMNA_DEPOSITAR}') no fueron encontradas.")
        st.write("Columnas disponibles en el archivo:", list(df.columns))
        return None

    # --- FILTRADO: Buscar números que terminan en .01 ---
    
    # Asegurar que la columna 'Depositar' sea numérica
    df[COLUMNA_DEPOSITAR] = pd.to_numeric(df[COLUMNA_DEPOSITAR], errors='coerce')
    df_limpio = df.dropna(subset=[COLUMNA_DEPOSITAR])

    # Aplicar el filtro: encontrar valores cuyo residuo decimal es 0.01
    df_filtrado = df_limpio[
        (df_limpio[COLUMNA_DEPOSITAR] * 100).round(0) % 100 == 1
    ].copy()
    
    # --- AGRUPACIÓN Y SUMA POR INICIADOR ---
    
    # Agrupar por la columna 'Iniciador' y sumar los depósitos filtrados
    resultados_por_iniciador = df_filtrado.groupby(COLUMNA_INICIADOR)[COLUMNA_DEPOSITAR].sum().reset_index()
    
    return resultados_por_iniciador

# =======================================================
# 3. INTERFAZ DE STREAMLIT (Aspecto Visual)
# =======================================================

st.set_page_config(page_title="Analizador de Depósitos .01", layout="centered")

st.title("📊 Analizador Web de Depósitos de Iniciadores")
st.markdown("---")

st.subheader("1. Cargar Archivo de Excel")

# Widget para que el usuario suba el archivo
archivo_cargado = st.file_uploader(
    "Sube aquí tu archivo de Excel. Se acepta formato .xlsx (moderno) o .xls (antiguo).", 
    type=['xlsx', 'xls']
)

# Instrucciones visuales
st.info(f"El sistema buscará las columnas llamadas **'{COLUMNA_INICIADOR}'** y **'{COLUMNA_DEPOSITAR}'** y filtrará las entradas que terminan en **.01** para sumarlas.")

if archivo_cargado:
    st.subheader("2. Resultados del Análisis")
    
    # Llamar a la función de procesamiento
    with st.spinner('Analizando datos y aplicando filtros...'):
        resultados = procesar_datos_excel(archivo_cargado)
    
    if resultados is not None and not resultados.empty:
        
        # Calcular la suma total
        suma_total_final = resultados[COLUMNA_DEPOSITAR].sum()
        
        # Mostrar el resultado total en métricas
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
        
        # Renombrar la columna para mejor presentación
        resultados.columns = ['Iniciador', 'Suma Total Depósitos .01']
        
        # Mostrar los resultados en una tabla interactiva
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
