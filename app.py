import streamlit as st
import pandas as pd
import os

# === Configuración inicial ===
st.set_page_config(page_title="Gestor de Base de Datos", layout="wide")
st.title("📋 Gestor de Base Unificada")

BASE_FILE = "base_unificada.xlsx"
COLUMNAS_ESTANDAR = ["Número", "Nombre", "Dirección", "CUPS"]

# === Función para cargar base existente ===
def cargar_base():
    if os.path.exists(BASE_FILE):
        return pd.read_excel(BASE_FILE)
    else:
        return pd.DataFrame(columns=COLUMNAS_ESTANDAR)

# === Función para guardar base ===
def guardar_base(df):
    df.to_excel(BASE_FILE, index=False)

# === Pestañas ===
tab1, tab2 = st.tabs(["📥 Cargar y Mapear", "🔍 Buscar"])

# --- Pestaña 1: Cargar y mapear ---
with tab1:
    st.subheader("Subir nuevos archivos Excel")
    archivos = st.file_uploader("Selecciona uno o varios archivos", type=["xlsx", "xls"], accept_multiple_files=True)

    if archivos:
        for archivo in archivos:
            df_temp = pd.read_excel(archivo)

            st.write(f"**Archivo cargado:** {archivo.name}")
            st.dataframe(df_temp.head())

            # Mapear columnas
            mapeo = {}
            for col in df_temp.columns:
                nueva_col = st.selectbox(f"¿Qué representa '{col}'?", ["Ignorar"] + COLUMNAS_ESTANDAR, key=f"{archivo.name}_{col}")
                if nueva_col != "Ignorar":
                    mapeo[col] = nueva_col

            if st.button(f"Guardar datos de {archivo.name}", key=archivo.name):
                df_temp = df_temp.rename(columns=mapeo)
                df_temp = df_temp[[c for c in df_temp.columns if c in COLUMNAS_ESTANDAR]]

                base = cargar_base()
                base = pd.concat([base, df_temp], ignore_index=True)
                guardar_base(base)

                st.success(f"Datos de {archivo.name} agregados a la base unificada.")

# --- Pestaña 2: Buscar ---
with tab2:
    st.subheader("Buscar en la base unificada")
    base = cargar_base()

    if not base.empty:
        busqueda = st.text_input("Escribe para buscar en cualquier columna")
        if busqueda:
            resultados = base[base.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]
        else:
            resultados = base

        st.write(f"Se encontraron {len(resultados)} resultados")
        st.dataframe(resultados)

        # Descargar resultados
        st.download_button("⬇ Descargar resultados", data=resultados.to_excel(index=False), file_name="resultados.xlsx")
    else:
        st.warning("La base unificada está vacía. Sube archivos en la pestaña anterior.")
