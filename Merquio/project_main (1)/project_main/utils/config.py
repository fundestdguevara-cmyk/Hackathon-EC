import streamlit as st

def configure_page():
    """Configuración de la página de Streamlit"""
    st.set_page_config(
        page_title="Samsung Merquio - Supply Chain Analytics",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded"
    )