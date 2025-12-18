import streamlit as st
import base64
from PIL import Image
import io
import os
import pathlib
import pandas as pd
import subprocess
import sys
import re

try:
    from CHATBOT.app import render_chatbot
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'CHATBOT'))
    from app import render_chatbot

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="ZooData Vision - Panel de Control", layout="wide", page_icon="🌿")

# --- HEADER Y LOGOS ---
logo_path = "IMAGES/LOGO.jpeg"
banner_path = "IMAGES/banner-cloudforest.jpg"

if os.path.exists(logo_path) and os.path.exists(banner_path):
    banner_b64 = base64.b64encode(open(banner_path, 'rb').read()).decode()
    logo_b64 = base64.b64encode(open(logo_path, 'rb').read()).decode()
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; justify-content: space-between; width: 100%; margin-bottom: 20px;'>
            <img src='data:image/jpeg;base64,{banner_b64}' style='width: 100%; max-height: 160px; object-fit: cover; border-radius: 8px; margin-right: 20px;'>
            <img src='data:image/jpeg;base64,{logo_b64}' style='height: 155px; border-radius: 8px;'>
        </div>""",
        unsafe_allow_html=True
    )
elif os.path.exists(logo_path):
    st.image(logo_path, width=180)

st.title("ZooData Vision Platform")

tab1, tab2 = st.tabs(["Procesamiento de Imágenes", "Asistente IA (Chatbot)"])


with tab1:
    st.markdown("### Pipeline de Clasificación y Detección")
    st.write("Esta sección permite procesar imágenes de fauna silvestre y visualizar los resultados.")

    input_folder = st.text_input(
        "Ruta de la carpeta con imágenes a procesar",
        value="DATASET_PRUEBA",
        help="Especifique la ruta de la carpeta que contiene las imágenes a procesar."
    )

    if st.button("🚀 Procesar imágenes", type="primary"):
        st.info("Procesando imágenes, esto puede tardar varios minutos...")
        
        try:
            with open("prediction_pipeline.py", "r", encoding="utf-8") as f:
                code = f.read()
            
            code = re.sub(r'SOURCE_IMAGES = ".*"', f'SOURCE_IMAGES = "{input_folder}"', code)
            
            with open("prediction_pipeline_temp.py", "w", encoding="utf-8") as f:
                f.write(code)
            
            # Ejecutar pipeline 1
            result1 = subprocess.run([sys.executable, "prediction_pipeline_temp.py"], capture_output=True, text=True)
            
            if result1.returncode != 0:
                st.error(f"Error en prediction_pipeline.py:\n{result1.stderr}")
            else:
                # Modificar Inferencia.py temporalmente
                with open("Inferencia.py", "r", encoding="utf-8") as f:
                    code2 = f.read()
                
                code2 = re.sub(r'SOURCE_IMAGES = ".*"', f'SOURCE_IMAGES = "{input_folder}"', code2)
                
                with open("Inferencia_temp.py", "w", encoding="utf-8") as f:
                    f.write(code2)
                
                # Ejecutar pipeline 2
                result2 = subprocess.run([sys.executable, "Inferencia_temp.py"], capture_output=True, text=True)
                
                if result2.returncode != 0:
                    st.error(f"Error en Inferencia.py:\n{result2.stderr}")
                else:
                    st.success("✅ Imágenes procesadas correctamente.")
                    st.balloons()

        except Exception as e:
            st.error(f"Ocurrió un error inesperado: {e}")
        
        finally:
            # Limpieza de archivos temporales
            if os.path.exists("prediction_pipeline_temp.py"):
                os.remove("prediction_pipeline_temp.py")
            if os.path.exists("Inferencia_temp.py"):
                os.remove("Inferencia_temp.py")

    csv_path = pathlib.Path("RESULTS/predicciones.csv")
    if csv_path.exists():
        st.divider()
        df = pd.read_csv(csv_path)
        
        col_metrics1, col_metrics2 = st.columns(2)
        col_metrics1.metric("Total Imágenes Procesadas", len(df))
        col_metrics2.metric("Promedio Confianza", f"{df['confianza'].mean():.2f}")

        st.subheader("📋 Tabla de Predicciones")
        st.dataframe(df.head(10), width="stretch")

        st.subheader("🖼️ Visualización de Resultados")
        for idx, row in df.head(5).iterrows():
            with st.container():
                st.markdown(f"**Registro {idx+1}:** `{row['clase_predicha']}` (Confianza: {row['confianza']:.2%})")
                cols = st.columns(2)
                
                orig_path = row['archivo_parent']
                if os.path.exists(orig_path):
                    cols[0].image(orig_path, caption="Original", use_container_width=True)
                else:
                    cols[0].warning(f"No encontrada: {orig_path}")
                
                # Recorte
                crop_path = row['archivo']
                if os.path.exists(crop_path):
                    cols[1].image(crop_path, caption="Recorte Detectado", width=200)
                else:
                    cols[1].warning(f"No encontrado: {crop_path}")
                st.divider()

with tab2:
    render_chatbot()