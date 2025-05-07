# LTS LAB ANALYZER - VERSIÓN PROFESIONAL PEDAGÓGICA

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os

# CONFIGURACIÓN
st.set_page_config(page_title="LTS Lab Analyzer", layout="wide")
LOGO_PATH = "logopetrogas.png"

# ESTILO OSCURO Y FORMATO
st.markdown("""
    <style>
        .stApp { background-color: #1e1e1e; color: white; }
        .stButton>button, .stDownloadButton>button {
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 8px;
        }
        input, textarea, .stTextInput, .stTextArea {
            background-color: #2e2e2e !important;
            color: white !important;
        }
        .stSelectbox div, .stNumberInput input {
            background-color: #2e2e2e !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO CON LOGO
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=130)
with col2:
    st.title("🧪 LTS Lab Analyzer")
    st.markdown("Aplicación profesional y pedagógica para análisis de laboratorio en plantas LTS.")

# FUNCIONES PDF
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "INFORME DE ANÁLISIS DE LABORATORIO", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Confidencial - Uso interno PETROGAS", 0, 0, "C")

    def add_section(self, title, content):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, title, 0, 1)
        self.set_font("Arial", "", 10)
        if isinstance(content, dict):
            for k, v in content.items():
                self.cell(0, 8, f"{k}: {v}", 0, 1)
        else:
            self.multi_cell(0, 8, str(content))
        self.ln(2)

def exportar_pdf(nombre, operador, explicacion, resultados, observaciones):
    pdf = PDF()
    pdf.add_page()
    pdf.add_section("Operador", operador)
    pdf.add_section("Explicación técnica", explicacion)
    pdf.add_section("Resultados", resultados)
    pdf.add_section("Observaciones", observaciones or "Sin observaciones.")
    output = pdf.output(dest='S').encode('latin-1', errors='ignore')
    st.download_button("⬇️ Descargar informe PDF", data=BytesIO(output), file_name=nombre, mime="application/pdf")

# PÁGINA PRINCIPAL: SELECCIÓN DE ANÁLISIS
st.markdown("---")
analisis = st.selectbox("🔬 Seleccioná el tipo de análisis:", [
    "-- Seleccionar --",
    "Gas Natural",
    "Gasolina Estabilizada",
    "MEG",
    "TEG",
    "Agua Desmineralizada",
    "Aminas"
])

# MÓDULO: GAS NATURAL
if analisis == "Gas Natural":
    st.subheader("🔥 Análisis de Gas Natural")
    st.markdown("Se evalúan componentes críticos del gas natural para verificar cumplimiento con especificaciones de salida de PTG/TPFs.")

    st.latex("H_2S_{max} = 2.1\\ ppm \\quad\\quad CO_2_{max} = 2\\ \\%")
    st.markdown("**Importancia:** Altos niveles de H₂S o CO₂ provocan corrosión, toxicidad y problemas regulatorios.")
    
    h2s = st.number_input("H₂S (ppm)", 0.0, step=0.1)
    co2 = st.number_input("CO₂ (%)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador")
    obs = st.text_area("📝 Observaciones")

    if st.button("📊 Analizar Gas Natural"):
        cumple_h2s = "✅ Cumple" if h2s <= 2.1 else "❌ Fuera de especificación"
        cumple_co2 = "✅ Cumple" if co2 <= 2 else "❌ Fuera de especificación"
        resultados = {
            "H₂S (ppm)": f"{h2s} - {cumple_h2s}",
            "CO₂ (%)": f"{co2} - {cumple_co2}"
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))
        exportar_pdf(
            f"Informe_GasNatural_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador,
            "Evaluación de H₂S y CO₂ en gas natural tratado. Valores fuera de rango implican riesgo operativo y corrosión.",
            resultados,
            obs
        )



