# app.py — LTS Lab Analyzer (versión corregida)
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import os
from io import BytesIO

# Configuración
st.set_page_config(page_title="LTS Lab Analyzer", layout="wide")
st.title("🧪 Laboratorio de Planta LTS")
st.markdown("Sistema profesional de análisis y validación de laboratorio con informes PDF para plantas de tratamiento de gas natural.")

# Crear carpetas necesarias
modulos = ["gas_natural", "gasolina", "meg", "teg", "agua_demi"]
for m in modulos:
    os.makedirs(f"informes/{m}", exist_ok=True)

LOGO_PATH = "LOGO PETROBRAS.PNG"

# Clase PDF
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
        self.cell(0, 10, f"Operador: {operador}", 0, 1)
        self.ln(2)

    def add_explanation(self, texto):
        self.set_font('Arial', 'I', 9)
        self.multi_cell(0, 6, texto)
        self.ln(3)

    def add_results(self, resultados):
        self.set_font('Arial', '', 10)
        for k, v in resultados.items():
            self.cell(0, 8, f"{k}: {v}", 0, 1)
        self.ln(4)

    def add_observaciones(self, texto="Sin observaciones."):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 8, f"Observaciones: {texto}")
        self.ln(3)

# Selector principal
opcion = st.selectbox("🔍 Seleccioná el tipo de análisis:", [
    "-- Seleccionar --",
    "Gasolina Estabilizada",
    "MEG",
    "TEG",
    "Agua Desmineralizada"
])

# Función para generar y descargar PDF
def generar_pdf(nombre_archivo, operador, explicacion, resultados, obs, carpeta):
    pdf = PDF()
    pdf.add_page()
    pdf.add_operator(operador)
    pdf.add_explanation(explicacion)
    pdf.add_results(resultados)
    pdf.add_observaciones(obs)

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    buffer = BytesIO(pdf_bytes)

    st.download_button(
        label="⬇️ Descargar informe PDF",
        data=buffer,
        file_name=nombre_archivo,
        mime="application/pdf"
    )

# Gasolina
if opcion == "Gasolina Estabilizada":
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

        generar_pdf(
            nombre_archivo=f"Informe_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador=operador,
            explicacion="Evaluación de gasolina estabilizada: TVR, contenido de sales y densidad.",
            resultados=resultados,
            obs=obs,
            carpeta="gasolina"
        )

# MEG
elif opcion == "MEG":
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

        generar_pdf(
            nombre_archivo=f"Informe_MEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            operador=operador,
            explicacion="Análisis de monoetilenglicol (MEG) utilizado como inhibidor de hidratos en plantas de gas.",
            resultados=resultados,
            obs=obs,
            carpeta="meg"
        )

# TEG
elif opcion == "TEG":
    st.subheader("🧪 Análisis de TEG")
    ph = st.number_input("pH", 0.0, 14.0, step=0.01)
    conc = st.number_input("Concentración (%)", 0.0, 100.0, step=0.1)
    dens = st.number_input("Densidad (kg/m³)", 0.0, step=0.1)
    cl = st.number_input("Cloruros (mg/L)", 0.0, step=0.1)
    hierro = st.number_input("Hierro (ppm)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador")
    obs = st.text_area("Observaciones")

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

# Agua Desmineralizada
elif opcion == "Agua Desmineralizada":
    st.subheader("💧 Análisis de Agua Desmineralizada")
    ph = st.number_input("pH", 0.0, 14.0, step=0.01)
    cl = st.number_input("Cloruros (mg/L)", 0.0, step=0.1)
    operador = st.text_input("👤 Operador")
    obs = st.text_area("Observaciones")

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

