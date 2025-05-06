# Ptg
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import io
import os
from datetime import datetime

# Configuración de la app
st.set_page_config(page_title="LTS Lab Analyzer", layout="wide")
st.title("🧪 Laboratorio de Planta LTS")

# Crear carpetas si no existen
os.makedirs("informes/gas_natural", exist_ok=True)

# Selector de análisis
opcion = st.selectbox("🔍 ¿Qué análisis desea realizar?", [
    "-- Seleccionar --",
    "Gas Natural",
    "Gasolina Estabilizada",
    "MEG",
    "Agua Desmineralizada"
])

# Propiedades de los componentes del gas
PM = {
    'CH4': 16.04, 'C2H6': 30.07, 'C3H8': 44.10,
    'i-C4H10': 58.12, 'n-C4H10': 58.12, 'i-C5H12': 72.15, 'n-C5H12': 72.15,
    'C6+': 86.00, 'N2': 28.01, 'CO2': 44.01, 'H2S': 34.08, 'O2': 32.00
}
HHV = {
    'CH4': 39.82, 'C2H6': 70.6, 'C3H8': 101.0,
    'i-C4H10': 131.6, 'n-C4H10': 131.6,
    'i-C5H12': 161.0, 'n-C5H12': 161.0,
    'C6+': 190.0
}
R = 8.314
PM_aire = 28.96
T_std = 288.15
P_std = 101325

# Función para análisis de composición
def analizar_composicion(composicion):
    composicion = {k: float(v) for k, v in composicion.items() if k in PM}
    total = sum(composicion.values())
    fracciones = {k: v / total for k, v in composicion.items()}
    pm_muestra = sum(fracciones[k] * PM[k] for k in fracciones)
    densidad = (pm_muestra * P_std) / (R * T_std)
    hhv_total = sum(fracciones.get(k, 0) * HHV.get(k, 0) for k in HHV)
    gamma = PM_aire / pm_muestra
    wobbe = hhv_total / np.sqrt(pm_muestra / PM_aire)
    dew_point = -30 if fracciones.get('C6+', 0) > 0.01 else -60
    api_h2s_ppm = composicion.get('H2S', 0) * 1e4
    carga_h2s = (api_h2s_ppm * PM['H2S'] / 1e6) / (pm_muestra * 1e3)
    ingreso = hhv_total * 2.25
    return {
        'PM': pm_muestra,
        'PCS (MJ/m3)': hhv_total,
        'PCS (kcal/m3)': hhv_total * 239.006,
        'Gamma': gamma,
        'Wobbe': wobbe,
        'Densidad (kg/m3)': densidad,
        'Dew Point estimado (°C)': dew_point,
        'CO2 (%)': composicion.get('CO2', 0),
        'H2S ppm': api_h2s_ppm,
        'Carga H2S (kg/kg)': carga_h2s,
        'Ingreso estimado (USD/m3)': ingreso
    }

# Clase para generar PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Análisis de Gas Natural', 0, 1, 'C')
        self.ln(5)

    def add_explanation(self, explicacion):
        self.set_font('Arial', '', 10)
        for linea in explicacion:
            self.multi_cell(0, 8, linea)
        self.ln(4)

    def add_sample(self, operador, resultados):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Operador: {operador}", 0, 1)
        for k, v in resultados.items():
            val = f"{v:.4f}" if isinstance(v, float) else v
            self.cell(0, 8, f"{k}: {val}", 0, 1)
        self.ln(3)

explicacion_gas = [
    "Este análisis calcula propiedades del gas natural a partir de su composición molar:",
    "- PM (peso molecular): promedio ponderado de los componentes.",
    "- PCS (poder calorífico superior): energía por m³.",
    "- Wobbe: importante para el diseño de quemadores.",
    "- Gamma: relación con el aire.",
    "- Dew Point: indica si hay riesgo de condensación.",
    "- H2S ppm: contenido de sulfuro de hidrógeno.",
    "- Ingreso estimado: valor económico aproximado del gas.",
    "Las propiedades se validan según normas de calidad para transporte y venta."
]

# SUBPÁGINA: Gas Natural
if opcion == "Gas Natural":
    st.subheader("🛢️ Análisis de Propiedades del Gas Natural")
    st.markdown("Cargá el archivo CSV con la composición molar (%). Debe tener los siguientes encabezados:")
    st.code(", ".join(PM.keys()))

    archivo = st.file_uploader("📁 Cargar archivo CSV", type=["csv"])
    operador = st.text_input("👤 Ingresá tu nombre o el del operador")

    if archivo is not None:
        try:
            df = pd.read_csv(archivo)
            composicion = df.iloc[0].to_dict()
            resultados = analizar_composicion(composicion)

            st.success("✅ Resultados del análisis")
            st.dataframe(pd.DataFrame.from_dict(resultados, orient='index', columns=['Valor']))

            # Generar PDF
            if st.button("📄 Descargar informe PDF"):
                pdf = PDF()
                pdf.add_page()
                pdf.add_explanation(explicacion_gas)
                pdf.add_sample(operador, resultados)

                nombre_pdf = f"Informe_Gas_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                ruta_pdf = f"informes/gas_natural/{nombre_pdf}"
                pdf.output(ruta_pdf)

                with open(ruta_pdf, "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar informe",
                        data=file,
                        file_name=nombre_pdf,
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
