import streamlit as st
import pandas as pd
from io import BytesIO

COLUMNA_INICIADOR = 'Iniciador' 
COLUMNA_DEPOSITAR = 'Depositar' 

def to_excel(df):
    """Convierte el DataFrame a Excel usando openpyxl (que ya tienes instalado)"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    return output.getvalue()

@st.cache_data(show_spinner=False)
def procesar_datos_excel(archivo_cargado):
    nombre_archivo = archivo_cargado.name.lower()
  
    motor = 'xlrd' if nombre_archivo.endswith('.xls') else 'openpyxl'
    try:
        df = pd.read_excel(archivo_cargado, engine=motor)
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        return None

    if COLUMNA_INICIADOR not in df.columns or COLUMNA_DEPOSITAR not in df.columns:
        st.error(f"❌ No se encontraron las columnas '{COLUMNA_INICIADOR}' y '{COLUMNA_DEPOSITAR} Habilita la edicion del Excel ❤️'.")
        return None
    
    df[COLUMNA_DEPOSITAR] = pd.to_numeric(df[COLUMNA_DEPOSITAR], errors='coerce')
    df_limpio = df.dropna(subset=[COLUMNA_DEPOSITAR])
    
   
    df_filtrado = df_limpio[
        (df_limpio[COLUMNA_DEPOSITAR] * 100).round(0) % 100 == 1
    ].copy()
    
    res = df_filtrado.groupby(COLUMNA_INICIADOR)[COLUMNA_DEPOSITAR].sum().reset_index()
    res.columns = [COLUMNA_INICIADOR, 'Suma']
    return res

st.set_page_config(page_title="Analizador Pro", layout="centered")

st.title("📊 Analizador de Depósitos .01")
st.markdown("---")

archivo = st.file_uploader("Carga tu Excel (.xls o .xlsx)", type=['xlsx', 'xls'])

if archivo:
    with st.spinner('Procesando datos...'):
        resultados = procesar_datos_excel(archivo)
    
    if resultados is not None and not resultados.empty:
        total_global = resultados['Suma'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Iniciadores Encontrados", len(resultados))
        c2.metric("Suma Total .01", f"{total_global:,.2f}")

        st.markdown("### 📋 Formato para Copiar y Pegar")
        
        texto_copiar = "📊 RESULTADOS AGRUPADOS POR INICIADOR ---\n"
        for _, fila in resultados.iterrows():
            texto_copiar += f"➡️ Iniciador: **{fila[COLUMNA_INICIADOR]}** | Suma de depósitos .01: **{fila['Suma']:,.2f}**\n"
        
        texto_copiar += f"\n⭐ SUMA TOTAL FINAL de todos los depósitos .01: **{total_global:,.2f}**"

        st.code(texto_copiar, language="markdown")

        st.markdown("---")

        st.subheader("Vista Detallada")
        st.dataframe(resultados, hide_index=True, use_container_width=True)
        
        st.download_button(
            label="⬇️ Descargar Resultados en Excel",
            data=to_excel(resultados),
            file_name='Analisis_Depositos.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    elif resultados is not None:
        st.warning("No se encontraron depósitos con terminación .01")



