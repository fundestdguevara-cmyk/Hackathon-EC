# components/dashboard.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def render_main_dashboard():  # <-- CAMBIAR NOMBRE
    """Crear dashboard principal con bienvenida"""
    st.title("🏭 Samsung Merquio - Supply Chain Analytics")
    
    st.markdown("""
    ## 📊 Dashboard Principal
    
    Bienvenido al sistema de análisis de cadena de suministro de Samsung Merquio.
    Esta plataforma integra todas las funcionalidades de análisis predictivo del negocio.
    """)
    
    # Información del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Disponible", "Online", "✅")
    
    with col2:
        st.metric("Versión", "1.0.0")
    
    with col3:
        data_status = "Cargado" if st.session_state.get('data_loaded', False) else "Por cargar"
        st.metric("Datos", data_status)
    
    with col4:
        st.metric("Usuarios", "1")
    
    st.markdown("---")
    
    st.header("🚀 Funcionalidades Disponibles")
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("### 👥 Análisis de Clientes")
        st.markdown("""
        - Detección de anomalías (Isolation Forest)
        - Segmentación por clusters (K-Prototypes)
        - Clasificación predictiva (Random Forest)
        """)
        st.info("Desde el menú: Análisis de Clientes")
    
    with cols[1]:
        st.markdown("### 🌍 Análisis Geográfico")
        st.markdown("""
        - Predicción por región
        - Análisis por país/estado
        - Segmentación territorial
        - Mapas interactivos
        """)
        st.info("Desde el menú: Análisis Geográfico")
    
    with cols[2]:
        st.markdown("### 📈 Predicción de Churn")
        st.markdown("""
        - Riesgo de abandono
        - Valor de vida (CLV)
        - Estrategias de retención
        - Segmentación por valor
        """)
        st.info("Desde el menú: Predicción de Churn")
    
    st.markdown("---")
    
    # Guía de inicio rápido
    st.header("📋 Guía de Inicio Rápido")
    
    st.markdown("""
    1. **Navega** a "Análisis de Clientes" desde el menú lateral
    2. **Carga los datos** usando el botón "Cargar y Procesar Datos"
    3. **Explora las funcionalidades**:
       - Detección de anomalías
       - Clustering de clientes
       - Clasificación de nuevos clientes
    4. **Analiza geográficamente** en la sección correspondiente
    5. **Predice churn** para estrategias de retención
    """)