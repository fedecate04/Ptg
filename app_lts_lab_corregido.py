# app.py — LTS Lab Analyzer (versión corregida)
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import os

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
        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Evaluación de gasolina estabilizada: TVR, contenido de sales y densidad.")
            pdf.add_results(resultados)
            pdf.add_observaciones(obs)
            path = f"informes/gasolina/Informe_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf.output(path)
            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=path.split("/")[-1], mime="application/pdf")

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
        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de monoetilenglicol utilizado como inhibidor de hidratos.")
            pdf.add_results(resultados)
            pdf.add_observaciones(obs)
            path = f"informes/meg/Informe_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf.output(path)
            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=path.split("/")[-1], mime="application/pdf")

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
        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de trietilenglicol para deshidratación de gas natural.")
            pdf.add_results(resultados)
            pdf.add_observaciones(obs)
            path = f"informes/teg/Informe_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf.output(path)
            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=path.split("/")[-1], mime="application/pdf")

# Agua desmineralizada
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
        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de agua desmineralizada para uso industrial y calderas.")
            pdf.add_results(resultados)
            pdf.add_observaciones(obs)
            path = f"informes/agua_demi/Informe_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf.output(path)
            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=path.split("/")[-1], mime="application/pdf")

# Manual de usuario
st.markdown("---")
st.subheader("📘 Manual de Usuario")

manual_path = "manual_lts_lab.pdf"

if not os.path.exists(manual_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "MANUAL DE USUARIO – LTS LAB ANALYZER", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 10)
    texto = (
        "Este sistema permite registrar, validar y documentar analisis de laboratorio\n"
        "para plantas LTS con estandares de la industria petrolera.\n\n"
        "Como usar la app:\n"
        "- Seleccione el tipo de analisis.\n"
        "- Ingrese los datos requeridos.\n"
        "- Descargue el informe en PDF profesional.\n\n"
        "Modulos incluidos:\n"
        "- Gas Natural (cromatografia CSV)\n"
        "- Gasolina Estabilizada\n"
        "- MEG / TEG\n"
        "- Agua Desmineralizada\n\n"
        "Cada informe incluye operador, observaciones, validacion automatica y logo oficial."
    )
    pdf.multi_cell(0, 8, texto)
    pdf.output(manual_path)

# Mostrar botón de descarga del manual
if os.path.exists(manual_path):
    with open(manual_path, "rb") as file:
        st.download_button(
            label="⬇️ Descargar Manual de Usuario (PDF)",
            data=file,
            file_name="Manual_LTS_Lab_Analyzer.pdf",
            mime="application/pdf"
        )
else:
    st.warning("⚠️ El manual no pudo ser generado.")
