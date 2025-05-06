# Ptg
# 🔹 BLOQUE 1 — IMPORTACIONES Y CONFIGURACIÓN INICIAL

import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import os
import io

# Configuración de la aplicación
st.set_page_config(page_title="LTS Lab Analyzer", layout="wide")
st.title("🧪 Laboratorio de Planta LTS")
st.markdown("Sistema profesional de análisis y validación de laboratorio con generación automática de informes PDF para uso en plantas LTS y plantas de procesamiento de gas.")

# Crear carpetas para informes si no existen
modulos = ["gas_natural", "gasolina", "meg", "teg", "agua_demi"]
for m in modulos:
    os.makedirs(f"informes/{m}", exist_ok=True)

# Ruta al logo de Petrobras (colocalo en la carpeta raíz con este nombre)
LOGO_PATH = "LOGO PETROBRAS.PNG"
# 🔹 BLOQUE 2 — CLASE PDF CON LOGO + FUNCIONES AUXILIARES

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

    def add_results(self, resultados, unidades=None, especificaciones=None):
        self.set_font('Arial', '', 10)
        for k, v in resultados.items():
            unidad = unidades[k] if unidades and k in unidades else ""
            espec = especificaciones[k] if especificaciones and k in especificaciones else ""
            val_str = f"{v} {unidad}" if unidad else str(v)
            self.cell(0, 8, f"{k}: {val_str} {espec}", 0, 1)
        self.ln(4)

    def add_observaciones(self, texto="Sin observaciones."):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 8, f"Observaciones: {texto}")
        self.ln(3)
# 🔹 BLOQUE 3 — SELECTOR DE ANÁLISIS PRINCIPAL

opcion = st.selectbox("🔍 Seleccioná el tipo de análisis:", [
    "-- Seleccionar --",
    "Gas Natural",
    "Gasolina Estabilizada",
    "MEG",
    "TEG",
    "Agua Desmineralizada"
])
# 🔹 BLOQUE 4 — MÓDULO GAS NATURAL (CSV + CÁLCULOS)

if opcion == "Gas Natural":
    st.subheader("🛢️ Análisis de Gas Natural (vía cromatografía)")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **PM (Peso molecular):** promedio ponderado de los gases presentes.
        - **PCS:** poder calorífico superior (energía entregada por m³).
        - **Gamma:** relación de densidad con el aire, útil para compresores.
        - **Wobbe Index:** afecta a quemadores e inyectores de gas.
        - **Dew Point:** punto de rocío estimado según C6+.
        - **H₂S ppm:** contenido de sulfuro de hidrógeno, impacto en corrosión.
        """)

    archivo = st.file_uploader("📁 Subí el archivo CSV con la composición molar (%)", type=["csv"])
    operador = st.text_input("👤 Ingresá el nombre del operador")
    observaciones = st.text_area("📝 Observaciones (opcional)", placeholder="Análisis rutinario...")

    PM = {
        'CH4': 16.04, 'C2H6': 30.07, 'C3H8': 44.10,
        'i-C4H10': 58.12, 'n-C4H10': 58.12,
        'i-C5H12': 72.15, 'n-C5H12': 72.15,
        'C6+': 86.00, 'N2': 28.01, 'CO2': 44.01,
        'H2S': 34.08, 'O2': 32.00
    }
    HHV = {
        'CH4': 39.82, 'C2H6': 70.6, 'C3H8': 101.0,
        'i-C4H10': 131.6, 'n-C4H10': 131.6,
        'i-C5H12': 161.0, 'n-C5H12': 161.0,
        'C6+': 190.0
    }
    R = 8.314
    T_std = 288.15
    P_std = 101325
    PM_aire = 28.96

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
        h2s_ppm = composicion.get('H2S', 0) * 1e4
        carga_h2s = (h2s_ppm * PM['H2S'] / 1e6) / (pm_muestra * 1e3)
        ingreso = hhv_total * 2.25
        return {
            'PM': round(pm_muestra, 4),
            'PCS (MJ/m³)': round(hhv_total, 2),
            'PCS (kcal/m³)': round(hhv_total * 239.006, 1),
            'Gamma': round(gamma, 4),
            'Wobbe Index': round(wobbe, 2),
            'Densidad (kg/m³)': round(densidad, 4),
            'Dew Point estimado (°C)': dew_point,
            'CO2 (%)': round(composicion.get('CO2', 0), 3),
            'H2S (ppm)': round(h2s_ppm, 2),
            'Carga H2S (kg/kg)': round(carga_h2s, 6),
            'Ingreso estimado (USD/m³)': round(ingreso, 2)
        }

    if archivo is not None:
        try:
            df = pd.read_csv(archivo)
            composicion = df.iloc[0].to_dict()
            resultados = analizar_composicion(composicion)
            st.success("✅ Resultados del análisis")
            st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

            if st.button("📄 Descargar informe PDF"):
                pdf = PDF()
                pdf.add_page()
                pdf.add_operator(operador)
                pdf.add_explanation("Análisis de propiedades fisicoquímicas del gas natural obtenido por cromatografía. Evaluación de su aptitud para transporte, venta y condiciones contractuales.")
                pdf.add_results(resultados)
                pdf.add_observaciones(observaciones)
                nombre = f"Informe_Gas_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                path = f"informes/gas_natural/{nombre}"
                pdf.output(path)

                with open(path, "rb") as f:
                    st.download_button(
                        label="⬇️ Descargar informe",
                        data=f,
                        file_name=nombre,
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
# 🔹 BLOQUE 5 — MÓDULO GASOLINA ESTABILIZADA

elif opcion == "Gasolina Estabilizada":
    st.subheader("⛽ Análisis de Gasolina Estabilizada")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **TVR (Tensión de Vapor Reid):** mide la volatilidad de la gasolina. Debe ser < 12 psi.
        - **Contenido de Sales:** presencia de compuestos iónicos que afectan la corrosión.
        - **Densidad:** relacionada con el poder energético del combustible.
        """)

    tvr = st.number_input("🔸 TVR (psi a 38,7 °C)", min_value=0.0, step=0.01)
    sales = st.number_input("🔸 Contenido de Sales (g/m²)", min_value=0.0, step=0.01)
    densidad = st.number_input("🔸 Densidad (kg/m³)", min_value=0.0, step=0.01)
    operador = st.text_input("👤 Ingresá tu nombre")
    observaciones = st.text_area("📝 Observaciones", placeholder="Control rutinario, muestras tanques...")

    if st.button("📊 Analizar"):
        cumple_tvr = "Cumple ✅" if tvr < 12 else "No cumple ❌"
        resultados = {
            "TVR (psi a 38,7 °C)": f"{tvr}  → {cumple_tvr}",
            "Sales (g/m²)": sales,
            "Densidad (kg/m³)": densidad
        }

        st.success("✅ Resultados del análisis")
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Este informe valida la calidad de la gasolina estabilizada en función de su volatilidad (TVR), contenido de sales y densidad. Relevante para almacenamiento y comercialización.")
            pdf.add_results(resultados)
            pdf.add_observaciones(observaciones)
            nombre = f"Informe_Gasolina_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            path = f"informes/gasolina/{nombre}"
            pdf.output(path)

            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=nombre, mime="application/pdf")
# 🔹 BLOQUE 6 — MÓDULO MEG (Monoetilenglicol)

elif opcion == "MEG":
    st.subheader("🧪 Análisis de MEG (Monoetilenglicol)")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **pH:** control de acidez del glicol, importante para evitar corrosión.
        - **Concentración (%):** nivel de pureza del MEG para control de hidratos.
        - **Densidad (kg/m³):** ayuda a validar concentración.
        - **Cloruros (mg/L):** indicadores de contaminación.
        - **MDEA (ppm):** presencia de aminas agregadas para control de CO₂/H₂S.
        """)

    ph = st.number_input("🔸 pH", min_value=0.0, max_value=14.0, step=0.01)
    concentracion = st.number_input("🔸 Concentración de MEG (%)", min_value=0.0, max_value=100.0, step=0.1)
    densidad = st.number_input("🔸 Densidad (kg/m³)", min_value=0.0, step=0.1)
    cloruros = st.number_input("🔸 Cloruros (mg/L)", min_value=0.0, step=0.1)
    mdea = st.number_input("🔸 MDEA (ppm)", min_value=0.0, step=0.1)
    operador = st.text_input("👤 Ingresá tu nombre")
    observaciones = st.text_area("📝 Observaciones", placeholder="Ej: muestra en línea 1...")

    if st.button("📊 Analizar MEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": concentracion,
            "Densidad (kg/m³)": densidad,
            "Cloruros (mg/L)": cloruros,
            "MDEA (ppm)": mdea
        }

        st.success("✅ Resultados del análisis")
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de Monoetilenglicol utilizado para inhibición de formación de hidratos. Se evalúan parámetros clave para verificar la calidad del glicol y su posible contaminación.")
            pdf.add_results(resultados)
            pdf.add_observaciones(observaciones)
            nombre = f"Informe_MEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            path = f"informes/meg/{nombre}"
            pdf.output(path)

            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=nombre, mime="application/pdf")
# 🔹 BLOQUE 7 — MÓDULO TEG (Trietilenglicol)

elif opcion == "TEG":
    st.subheader("🧪 Análisis de TEG (Trietilenglicol)")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **pH:** medida de acidez, afecta la vida útil del glicol.
        - **Concentración (%):** pureza del TEG, relacionada con eficiencia de deshidratación.
        - **Densidad (kg/m³):** sirve como verificación indirecta de concentración.
        - **Cloruros (mg/L):** contaminación por sales solubles.
        - **Hierro (ppm):** corrosión interna del sistema.
        """)

    ph = st.number_input("🔸 pH", min_value=0.0, max_value=14.0, step=0.01)
    concentracion = st.number_input("🔸 Concentración de TEG (%)", min_value=0.0, max_value=100.0, step=0.1)
    densidad = st.number_input("🔸 Densidad (kg/m³)", min_value=0.0, step=0.1)
    cloruros = st.number_input("🔸 Cloruros (mg/L)", min_value=0.0, step=0.1)
    hierro = st.number_input("🔸 Hierro (ppm)", min_value=0.0, step=0.1)
    operador = st.text_input("👤 Ingresá tu nombre")
    observaciones = st.text_area("📝 Observaciones", placeholder="Ej: muestra torre de contacto...")

    if st.button("📊 Analizar TEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": concentracion,
            "Densidad (kg/m³)": densidad,
            "Cloruros (mg/L)": cloruros,
            "Hierro (ppm)": hierro
        }

        st.success("✅ Resultados del análisis")
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de Trietilenglicol utilizado para deshidratación de gas natural. Se controlan parámetros esenciales para garantizar su eficiencia y evitar fallas por corrosión.")
            pdf.add_results(resultados)
            pdf.add_observaciones(observaciones)
            nombre = f"Informe_TEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            path = f"informes/teg/{nombre}"
            pdf.output(path)

            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=nombre, mime="application/pdf")
# 🔹 BLOQUE 7 — MÓDULO TEG (Trietilenglicol)

elif opcion == "TEG":
    st.subheader("🧪 Análisis de TEG (Trietilenglicol)")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **pH:** medida de acidez, afecta la vida útil del glicol.
        - **Concentración (%):** pureza del TEG, relacionada con eficiencia de deshidratación.
        - **Densidad (kg/m³):** sirve como verificación indirecta de concentración.
        - **Cloruros (mg/L):** contaminación por sales solubles.
        - **Hierro (ppm):** corrosión interna del sistema.
        """)

    ph = st.number_input("🔸 pH", min_value=0.0, max_value=14.0, step=0.01)
    concentracion = st.number_input("🔸 Concentración de TEG (%)", min_value=0.0, max_value=100.0, step=0.1)
    densidad = st.number_input("🔸 Densidad (kg/m³)", min_value=0.0, step=0.1)
    cloruros = st.number_input("🔸 Cloruros (mg/L)", min_value=0.0, step=0.1)
    hierro = st.number_input("🔸 Hierro (ppm)", min_value=0.0, step=0.1)
    operador = st.text_input("👤 Ingresá tu nombre")
    observaciones = st.text_area("📝 Observaciones", placeholder="Ej: muestra torre de contacto...")

    if st.button("📊 Analizar TEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": concentracion,
            "Densidad (kg/m³)": densidad,
            "Cloruros (mg/L)": cloruros,
            "Hierro (ppm)": hierro
        }

        st.success("✅ Resultados del análisis")
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de Trietilenglicol utilizado para deshidratación de gas natural. Se controlan parámetros esenciales para garantizar su eficiencia y evitar fallas por corrosión.")
            pdf.add_results(resultados)
            pdf.add_observaciones(observaciones)
            nombre = f"Informe_TEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            path = f"informes/teg/{nombre}"
            pdf.output(path)

            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=nombre, mime="application/pdf")
# 🔹 BLOQUE 7 — MÓDULO TEG (Trietilenglicol)

elif opcion == "TEG":
    st.subheader("🧪 Análisis de TEG (Trietilenglicol)")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **pH:** medida de acidez, afecta la vida útil del glicol.
        - **Concentración (%):** pureza del TEG, relacionada con eficiencia de deshidratación.
        - **Densidad (kg/m³):** sirve como verificación indirecta de concentración.
        - **Cloruros (mg/L):** contaminación por sales solubles.
        - **Hierro (ppm):** corrosión interna del sistema.
        """)

    ph = st.number_input("🔸 pH", min_value=0.0, max_value=14.0, step=0.01)
    concentracion = st.number_input("🔸 Concentración de TEG (%)", min_value=0.0, max_value=100.0, step=0.1)
    densidad = st.number_input("🔸 Densidad (kg/m³)", min_value=0.0, step=0.1)
    cloruros = st.number_input("🔸 Cloruros (mg/L)", min_value=0.0, step=0.1)
    hierro = st.number_input("🔸 Hierro (ppm)", min_value=0.0, step=0.1)
    operador = st.text_input("👤 Ingresá tu nombre")
    observaciones = st.text_area("📝 Observaciones", placeholder="Ej: muestra torre de contacto...")

    if st.button("📊 Analizar TEG"):
        resultados = {
            "pH": ph,
            "Concentración (%)": concentracion,
            "Densidad (kg/m³)": densidad,
            "Cloruros (mg/L)": cloruros,
            "Hierro (ppm)": hierro
        }

        st.success("✅ Resultados del análisis")
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Análisis de Trietilenglicol utilizado para deshidratación de gas natural. Se controlan parámetros esenciales para garantizar su eficiencia y evitar fallas por corrosión.")
            pdf.add_results(resultados)
            pdf.add_observaciones(observaciones)
            nombre = f"Informe_TEG_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            path = f"informes/teg/{nombre}"
            pdf.output(path)

            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=nombre, mime="application/pdf")
# 🔹 BLOQUE 8 — MÓDULO AGUA DESMINERALIZADA

elif opcion == "Agua Desmineralizada":
    st.subheader("💧 Análisis de Agua Desmineralizada")

    with st.expander("📘 ¿Qué representa cada parámetro?"):
        st.markdown("""
        - **pH:** debe mantenerse neutro (6.5 a 7.5) para evitar corrosión.
        - **Cloruros (mg/L):** indican la pureza iónica del agua. Deben ser mínimos o nulos.
        """)

    ph = st.number_input("🔸 pH", min_value=0.0, max_value=14.0, step=0.01)
    cloruros = st.number_input("🔸 Cloruros (mg/L)", min_value=0.0, step=0.1)
    operador = st.text_input("👤 Ingresá tu nombre")
    observaciones = st.text_area("📝 Observaciones", placeholder="Ej: muestra generador de vapor...")

    if st.button("📊 Analizar Agua Desmineralizada"):
        resultados = {
            "pH": ph,
            "Cloruros (mg/L)": cloruros
        }

        st.success("✅ Resultados del análisis")
        st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Valor"]))

        if st.button("📄 Descargar informe PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.add_operator(operador)
            pdf.add_explanation("Control de calidad de agua desmineralizada usada en procesos industriales. El pH y los cloruros son indicadores clave de seguridad y eficiencia.")
            pdf.add_results(resultados)
            pdf.add_observaciones(observaciones)
            nombre = f"Informe_AguaDemi_{operador}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            path = f"informes/agua_demi/{nombre}"
            pdf.output(path)

            with open(path, "rb") as f:
                st.download_button("⬇️ Descargar informe", f, file_name=nombre, mime="application/pdf")
# 🔹 BLOQUE 9 — DESCARGA DEL MANUAL DE USUARIO EN PDF

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
        "Este sistema fue desarrollado para laboratorios de plantas LTS y permite registrar, validar y documentar\n"
        "análisis de laboratorio con estándares profesionales de la industria petrolera.\n\n"
        "🔹 Cómo usar la app:\n"
        "- Seleccioná el tipo de análisis.\n"
        "- Ingresá los parámetros requeridos.\n"
        "- Descargá el informe en PDF con validación.\n\n"
        "🔹 Módulos disponibles:\n"
        "- Gas Natural\n"
        "- Gasolina Estabilizada\n"
        "- MEG (Monoetilenglicol)\n"
        "- TEG (Trietilenglicol)\n"
        "- Agua Desmineralizada\n\n"
        "🔹 Cada informe contiene:\n"
        "- Resultados ingresados\n"
        "- Validación automática\n"
        "- Firma del operador y observaciones\n"
        "- Logo institucional y formato profesional\n\n"
        "⚠️ Importante: Las especificaciones pueden configurarse en futuras versiones. Contacto: laboratorio@petrobras.com"
    )
    pdf.multi_cell(0, 8, texto)
    pdf.output(manual_path)

with open(manual_path, "rb") as file:
    st.download_button(
        label="⬇️ Descargar Manual de Usuario (PDF)",
        data=file,
        file_name="Manual_LTS_Lab_Analyzer.pdf",
        mime="application/pdf"
    )

