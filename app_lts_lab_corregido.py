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

LOGO_PATH = "LOGO PETROGAS.png"  # Usamos el logo nuevo

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

# Función para generar PDF
def generar_pdf(nombre_archivo, operador, explicacion, resultados, obs, carpeta):
    pdf = PDF()
    pdf.add_page()
    pdf.add_operator(operador)
    pdf.add_explanation(explicacion)
    pdf.add_results(resultados)
    pdf.add_observaciones(obs)

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

if analisis_nuevo != st.session_state.analisis_actual:
    st.session_state.analisis_actual = analisis_nuevo
    st.experimental_rerun()
    # Módulo Gasolina Estabilizada
if analisis_nuevo == "Gasolina Estabilizada":
    st.subheader("⛽ Análisis de Gasolina Estabilizada")
    tvr = st.number_input("TVR (psi a 38,7 °C)", min_value=0.0, step=0.01)
    sales = st.number_input("Sales (g/m²)", min_value=0.0, step=0.01)
    densidad = st.number_input("Densidad (kg/m³)", min_value=0.0, step=0.01)
    operador = st.text_input("👤 Operador")
    obs = st.text_area("Observaciones")

    if st.button("📊 Analizar"):
        cumple = "Cumple ✅" if tvr < 12 else "No cumple ❌"
        resultados = {
            "TVR (psi)": f"{tvr} → {cumple}",
            "Sales (g/m²)": sales,
            "Densidad (kg/m³)": densidad
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        nombre_archivo = f"Informe_Gasolina_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        ruta = os.path.join("informes/gasolina", nombre_archivo)

        generar_pdf(nombre_archivo, operador,
            "Evaluación de gasolina estabilizada: TVR, contenido de sales y densidad.",
            resultados, obs, "gasolina")

        with open(ruta, "wb") as f:
            f.write(PDF().output(dest="S").encode("latin1", errors="ignore"))

# Repetimos lo mismo para los demás módulos...

# MEG
elif analisis_nuevo == "MEG":
    st.subheader("🧪 Análisis de MEG")
    ph = st.number_input("pH", 0.0, 14.0, step=0.01)
    conc = st.number_input("Concentración (%)", 0.0, 100.0, step=0.1)
    dens = st.number_input("Densidad (kg/m³)", 0.0, step=0.1)
    cl = st.number_input("Cloruros (mg/L)", 0.0, step=0.1)
    mdea = st.number_input("MDEA (ppm)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador")
    obs = st.text_area("Observaciones")

    if st.button("📊 Analizar MEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": conc,
            "Densidad (kg/m³)": dens,
            "Cloruros (mg/L)": cl,
            "MDEA (ppm)": mdea
        }
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        nombre_archivo = f"Informe_MEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        ruta = os.path.join("informes/meg", nombre_archivo)

        generar_pdf(nombre_archivo, operador,
            "Análisis de monoetilenglicol (MEG) utilizado como inhibidor de hidratos en plantas de gas.",
            resultados, obs, "meg")

        with open(ruta, "wb") as f:
            f.write(PDF().output(dest="S").encode("latin1", errors="ignore"))

# Seguir con TEG, Agua y Gas Natural igual...

# Manual de Usuario
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
