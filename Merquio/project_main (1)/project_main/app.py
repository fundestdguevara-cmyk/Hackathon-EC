# app.py - Versión simplificada
import streamlit as st
from components.sidebar import render_sidebar
from components.customer_analytics import render_customer_analytics
from components.geo_analytics import render_geo_analytics
from components.churn_analytics import render_churn_analytics
from components.dashboard import render_main_dashboard
from components.product_analytics import render_product_analytics  # Importar nuevo módulo

# Configuración básica
st.set_page_config(
    page_title="Samsung Merquio - Supply Chain Analytics",
    page_icon="🏭",
    layout="wide"
)

# Inicializar estado de sesión
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None

try:
    # Sidebar con navegación
    menu_option = render_sidebar()
    
    # Contenido principal basado en la selección
    if menu_option == "Dashboard Principal":
        render_main_dashboard()
        
    elif menu_option == "Análisis de Clientes":
        render_customer_analytics()
        
    elif menu_option == "Análisis Geográfico":
        render_geo_analytics()
        
    elif menu_option == "Predicción de Churn":
        render_churn_analytics()
        
    elif menu_option == "Análisis de Productos":
        render_product_analytics()
        
    else:
        st.error(f"Opción no válida: {menu_option}")
        
except Exception as e:
    st.error(f"Error en la aplicación: {str(e)}")
    st.info("Para debuggear, revisa la consola o contacta al desarrollador.")