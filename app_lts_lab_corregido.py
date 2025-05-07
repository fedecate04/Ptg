import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import os
from io import BytesIO

# Configuración inicial
st.set_page_config(page_title="LTS Lab Analyzer", layout="wide")
st.title("🧪 Laboratorio de Planta LTS")
st.markdown("Sistema profesional de análisis y validación de laboratorio con informes PDF para plantas de tratamiento de gas natural.")

# Crear carpetas de informes
modulos = ["gas_natural", "gasolina", "meg", "teg", "agua_demi"]
for m in modulos:
    os.makedirs(f"informes/{m}", exist_ok=True)

LOGO_PATH = "LOGO PETROGAS.png"  # Asegurate de que el PNG esté en RGB (sin transparencia)

# Función para limpiar caracteres no compatibles con latin1
def limpiar_texto(texto):
    return texto.replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"')

# Clase PDF personalizada
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'INFORME DE ANÁLISIS DE LABORATORIO', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Confidencial - Uso interno Petrobras LTS', 0, 0, 'C')

    def add_operator(self, operador):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Operador: {limpiar_texto(operador)}", 0, 1)
        self.ln(2)

    def add_explanation(self, texto):
        self.set_font('Arial', 'I', 9)
        self.multi_cell(0, 6, limpiar_texto(texto))
        self.ln(3)

    def add_results(self, resultados):
        self.set_font('Arial', '', 10)
        for k, v in resultados.items():
            k_clean = limpiar_texto(str(k))
            v_clean = limpiar_texto(str(v))
            self.cell(0, 8, f"{k_clean}: {v_clean}", 0, 1)
        self.ln(4)

    def add_observaciones(self, texto="Sin observaciones."):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 8, f"Observaciones: {limpiar_texto(texto)}")
        self.ln(3)
      # Función para generar y guardar PDF
def generar_pdf(nombre_archivo, operador, explicacion, resultados, obs, carpeta):
    pdf = PDF()
    pdf.add_page()
    pdf.add_operator(operador)
    pdf.add_explanation(explicacion)
    pdf.add_results(resultados)
    pdf.add_observaciones(obs)

    # Guardar automáticamente en carpeta del módulo
    ruta = os.path.join(f"informes/{carpeta}", nombre_archivo)
    pdf.output(ruta, 'F')

    # Preparar para descarga
    pdf_bytes = pdf.output(dest="S").encode("latin1", errors="ignore")
    buffer = BytesIO(pdf_bytes)

    st.download_button(
        label="⬇️ Descargar informe PDF",
        data=buffer,
        file_name=nombre_archivo,
        mime="application/pdf"
    )

# Manejo del cambio de análisis
if "analisis_actual" not in st.session_state:
    st.session_state.analisis_actual = "-- Seleccionar --"

analisis_nuevo = st.selectbox("🔍 Seleccioná el tipo de análisis:", [
    "-- Seleccionar --",
    "Gas Natural",
    "Gasolina Estabilizada",
    "MEG",
    "TEG",
    "Agua Desmineralizada"
], key="tipo_analisis")

# Reset automático al cambiar
if analisis_nuevo != st.session_state.analisis_actual:
    st.session_state.analisis_actual = analisis_nuevo
    for key in list(st.session_state.keys()):
        if key.startswith("operador_") or key.startswith("obs_"):
            del st.session_state[key]
   st.rerun() 

# MÓDULO: Gasolina Estabilizada
if analisis_nuevo == "Gasolina Estabilizada":
    st.subheader("⛽ Análisis de Gasolina Estabilizada")
    tvr = st.number_input("TVR (psi a 38,7 °C)", min_value=0.0, step=0.01)
    sales = st.number_input("Sales (g/m²)", min_value=0.0, step=0.01)
    densidad = st.number_input("Densidad (kg/m³)", min_value=0.0, step=0.01)
    operador = st.text_input("👤 Operador", key="operador_gasolina")
    obs = st.text_area("Observaciones", key="obs_gasolina")

    if st.button("📊 Analizar"):
        cumple = "Cumple ✅" if tvr < 12 else "No cumple ❌"
        resultados = {
            "TVR (psi)": f"{tvr} → {cumple}",
            "Sales (g/m²)": sales,
            "Densidad (kg/m³)": densidad
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        generar_pdf(
            nombre_archivo=f"Informe_Gasolina_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador=operador,
            explicacion="Evaluación de gasolina estabilizada: TVR, contenido de sales y densidad.",
            resultados=resultados,
            obs=obs,
            carpeta="gasolina"
        )

# MÓDULO: MEG
elif analisis_nuevo == "MEG":
    st.subheader("🧪 Análisis de MEG")
    ph = st.number_input("pH", 0.0, 14.0, step=0.01)
    conc = st.number_input("Concentración (%)", 0.0, 100.0, step=0.1)
    dens = st.number_input("Densidad (kg/m³)", 0.0, step=0.1)
    cl = st.number_input("Cloruros (mg/L)", 0.0, step=0.1)
    mdea = st.number_input("MDEA (ppm)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador", key="operador_meg")
    obs = st.text_area("Observaciones", key="obs_meg")

    if st.button("📊 Analizar MEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": conc,
            "Densidad (kg/m³)": dens,
            "Cloruros (mg/L)": cl,
            "MDEA (ppm)": mdea
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        generar_pdf(
            nombre_archivo=f"Informe_MEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador=operador,
            explicacion="Análisis de monoetilenglicol (MEG) utilizado como inhibidor de hidratos en plantas de gas.",
            resultados=resultados,
            obs=obs,
            carpeta="meg"
        )
        # MÓDULO: TEG
elif analisis_nuevo == "TEG":
    st.subheader("🧪 Análisis de TEG")
    ph = st.number_input("pH", 0.0, 14.0, step=0.01)
    conc = st.number_input("Concentración (%)", 0.0, 100.0, step=0.1)
    dens = st.number_input("Densidad (kg/m³)", 0.0, step=0.1)
    cl = st.number_input("Cloruros (mg/L)", 0.0, step=0.1)
    hierro = st.number_input("Hierro (ppm)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador", key="operador_teg")
    obs = st.text_area("Observaciones", key="obs_teg")

    if st.button("📊 Analizar TEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": conc,
            "Densidad (kg/m³)": dens,
            "Cloruros (mg/L)": cl,
            "Hierro (ppm)": hierro
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        generar_pdf(
            nombre_archivo=f"Informe_TEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador=operador,
            explicacion="Análisis de trietilenglicol (TEG) utilizado para deshidratación de gas natural.",
            resultados=resultados,
            obs=obs,
            carpeta="teg"
        )

# MÓDULO: Agua Desmineralizada
elif analisis_nuevo == "Agua Desmineralizada":
    st.subheader("💧 Análisis de Agua Desmineralizada")
    ph = st.number_input("pH", 0.0, 14.0, step=0.01)
    cl = st.number_input("Cloruros (mg/L)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador", key="operador_agua")
    obs = st.text_area("Observaciones", key="obs_agua")

    if st.button("📊 Analizar Agua"):
        resultados = {
            "pH": ph,
            "Cloruros (mg/L)": cl
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        generar_pdf(
            nombre_archivo=f"Informe_AguaDemi_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador=operador,
            explicacion="Análisis de agua desmineralizada para uso industrial, calderas o procesos sensibles.",
            resultados=resultados,
            obs=obs,
            carpeta="agua_demi"
        )

# MÓDULO: Gas Natural (desde CSV)
elif analisis_nuevo == "Gas Natural":
    st.subheader("🔥 Análisis de Gas Natural - Cromatografía")
    archivo = st.file_uploader("📁 Cargar archivo CSV de cromatografía", type=["csv"])
    operador = st.text_input("👤 Operador", key="operador_gas")
    obs = st.text_area("Observaciones", key="obs_gas")

    if archivo is not None:
        df = pd.read_csv(archivo)
        st.dataframe(df)

        resultado_ficticio = {
            "Metano (%)": df["Metano"].sum() if "Metano" in df.columns else "No disponible",
            "Etano (%)": df["Etano"].sum() if "Etano" in df.columns else "No disponible",
            "Poder calorífico (kcal/m³)": 9500,
            "Gravedad específica": 0.65
        }

        st.dataframe(pd.DataFrame(resultado_ficticio.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            generar_pdf(
                nombre_archivo=f"Informe_Gas_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                operador=operador,
                explicacion="Análisis de composición de gas natural a partir de cromatografía. Incluye poder calorífico y gravedad específica.",
                resultados=resultado_ficticio,
                obs=obs,
                carpeta="gas_natural"
            )

# MANUAL DE USUARIO
st.markdown("---")
st.subheader("📘 Manual de Usuario")

if st.button("📄 Generar Manual de Usuario"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "MANUAL DE USUARIO - LTS LAB ANALYZER", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 10)

    texto = (
        "Este sistema permite registrar, validar y documentar análisis de laboratorio\n"
        "para plantas LTS con estándares de la industria petrolera.\n\n"
        "📋 Cómo usar la app:\n"
        "- Seleccione el tipo de análisis.\n"
        "- Ingrese los datos requeridos o cargue el CSV.\n"
        "- Valide los parámetros.\n"
        "- Descargue el informe profesional en PDF con logo.\n\n"
        "🧪 Módulos incluidos:\n"
        "- Gas Natural (CSV cromatografía)\n"
        "- Gasolina Estabilizada\n"
        "- MEG / TEG\n"
        "- Agua Desmineralizada\n\n"
        "📄 Cada informe incluye: operador, validación, observaciones y diseño profesional."
    )

    pdf.multi_cell(0, 8, limpiar_texto(texto))

    pdf_bytes = pdf.output(dest='S').encode('latin1', errors="ignore")
    buffer = BytesIO(pdf_bytes)

    st.download_button(
        label="⬇️ Descargar Manual de Usuario (PDF)",
        data=buffer,
        file_name="Manual_LTS_Lab_Analyzer.pdf",
        mime="application/pdf"
    )
    
