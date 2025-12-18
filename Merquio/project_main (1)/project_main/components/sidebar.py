import streamlit as st
# components/sidebar.py - Asegurar que tiene la opción de productos
def render_sidebar():
    """Renderiza la barra lateral con navegación"""
    
    with st.sidebar:
        st.title("🏭 Samsung Merquio")
        st.markdown("---")
        
        # Menú de navegación
        st.markdown("### Navegación")
        
        # Opciones del menú - AGREGAR "Análisis de Productos"
        menu_options = [
            "Dashboard Principal",
            "Análisis de Clientes", 
            "Análisis Geográfico",
            "Predicción de Churn",
            "Análisis de Productos"  # ← NUEVA OPCIÓN
        ]
        
        selected = st.radio(
            "Selecciona una página",
            menu_options,
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("### Información")
        st.caption("Versión 1.0.0")
        st.caption("Supply Chain Analytics")
        
        return selected