"""Signify - Sistema de Tradución de Lengua de Señas

Aplicación web profesional para traducción y aprendizaje de señas.
Desarrollado con Streamlit para una interfaz moderna y accesible.

Autor: Signify Team
Versión: 2.0.0"""

import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

# Importar módulos del proyecto
from analysis.comparative_analysis import get_comparative_analyzer
from audio.speech_engine import get_speech_engine, get_voice_recognition
from core.sign_processor import SearchResult, get_processor
from database.signs_database import SignEntry, SignsDatabase
from webcam_integration import SignLanguagePredictor
import cv2

# Constantes de configuración
APP_TITLE = "Signify"
APP_ICON = "🤟"
APP_DESCRIPTION = "Sistema Profesional de Tradución de Lengua de Señas"

# CSS Variables - Tema profesional optimizado
CSS_VARIABLES = """
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --success-color: #C73E1D;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-background: rgba(255, 255, 255, 0.95);
        --text-primary: #2c3e50;
        --text-secondary: #2c3e50;
        --text-dark: #1a365d;
        --text-black: #000000;
        --background-white: #ffffff;
        --border-radius: 12px;
        --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.1);
        --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.15);
        --transition-smooth: all 0.3s ease;
        --gradient-primary: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        --gradient-accent: linear-gradient(135deg, var(--accent-color) 0%, #ff6b35 100%);
        --gradient-background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
    }
"""

# Configuración de la página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': f"{APP_TITLE} - {APP_DESCRIPTION}"
    }
)


def load_custom_css() -> None:
    """Carga estilos CSS personalizados para la interfaz profesional."""
    custom_css = f"""
    <style>
    /* Variables CSS para tema profesional */
    {CSS_VARIABLES}
    
    /* Fondo principal */
    .stApp {{
        background: var(--background-gradient);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Contenedor principal */
    .main-container {{
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 1rem;
        box-shadow: var(--shadow-soft);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    /* Estilos generales para texto - Consolidado */
    .stApp, .stApp *, p, span, div, label, .stMarkdown {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }}
    
    /* Títulos principales - Consolidado */
    h1, .main-title, .stApp h1 {{
        color: var(--text-dark) !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
        font-weight: 700 !important;
        background: none !important;
        -webkit-text-fill-color: var(--text-dark) !important;
    }}
    
    .main-title {{
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }}
    
    /* Títulos secundarios - Consolidado */
    h2, .feature-card h2 {{
        color: var(--text-dark) !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2) !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }}
    
    .subtitle {{
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }}
    
    /* Tarjetas de funcionalidad */
    .feature-card {{
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-soft);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }}
    
    .feature-card:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}
    
    /* Botones personalizados */
    .stButton > button {{
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: var(--transition-smooth);
        box-shadow: var(--shadow-soft);
        width: 100%;
    }}
    
    .stButton > button:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}
    
    /* Sidebar personalizada */
    .css-1d391kg {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }}
    
    /* Inputs personalizados - Optimizado */
    .stTextInput > div > div > input {{
        background-color: var(--background-white) !important;
        color: var(--text-black) !important;
        border-radius: var(--border-radius);
        border: 2px solid #e1e8ed;
        padding: 0.75rem;
        font-size: 1rem;
        transition: var(--transition-smooth);
    }}
    
    .stTextInput > div > div > input:focus {{
        background-color: var(--background-white) !important;
        color: var(--text-black) !important;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: var(--text-black) !important;
        opacity: 0.7;
    }}
    
    /* Selectbox - Fondo claro y legible, integrado con el tema */
    .stSelectbox > div > div > div {{
        background: var(--card-background) !important;
        color: var(--text-dark) !important;
        border: 1.5px solid rgba(102, 126, 234, 0.35) !important;
        border-radius: var(--border-radius) !important;
        box-shadow: var(--shadow-soft) !important;
        backdrop-filter: blur(8px) !important;
        transition: var(--transition-smooth) !important;
        outline: none !important;
    }}
    
    .stSelectbox > div > div > div:hover {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(245, 247, 252, 1) 100%) !important;
        box-shadow: var(--shadow-hover) !important;
        transform: translateY(-1px) !important;
        border-color: rgba(118, 75, 162, 0.55) !important;
    }}
    
    .stSelectbox > div > div > div > div {{
        background: transparent !important;
        color: var(--text-dark) !important;
        font-weight: 600 !important;
    }}
    
    /* Opciones del selectbox - mejoradas para legibilidad */
    .stSelectbox > div > div > div > div > div {{
        background: transparent !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(102, 126, 234, 0.15) !important;
        backdrop-filter: blur(6px) !important;
    }}
    
    .stSelectbox > div > div > div > div > div:hover {{
        background: var(--gradient-primary) !important;
        color: white !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35) !important;
        border-color: rgba(118, 75, 162, 0.45) !important;
    }}
    
    /* Dropdown del selectbox - fondo claro consistente */
    .stSelectbox [data-baseweb="select"] > div {{
        background: var(--card-background) !important;
        color: var(--text-primary) !important;
        border-radius: var(--border-radius) !important;
        backdrop-filter: blur(10px) !important;
        border: 1.5px solid rgba(102, 126, 234, 0.35) !important;
        box-shadow: var(--shadow-soft) !important;
    }}
    
    /* Texto seleccionado en selectbox - Optimizado */
    .stSelectbox [data-baseweb="select"] > div > div {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8) !important;
    }}
    
    /* Flecha del dropdown con mejor visibilidad */
    .stSelectbox [data-baseweb="select"] svg {{
        fill: var(--primary-color) !important;
        transition: var(--transition-smooth) !important;
    }}
    
    .stSelectbox [data-baseweb="select"]:hover svg {{
        fill: var(--secondary-color) !important;
        transform: scale(1.1) !important;
    }}
    
    /* Lista desplegable con sombra y bordes elegantes */
    .stSelectbox [data-baseweb="popover"] {{
        border-radius: var(--border-radius) !important;
        box-shadow: var(--shadow-hover) !important;
        border: 1.5px solid rgba(102, 126, 234, 0.35) !important;
        backdrop-filter: blur(12px) !important;
        background: var(--card-background) !important;
    }}
    
    /* Forzar fondo claro dentro del contenedor del menú */
    .stSelectbox [data-baseweb="popover"] > div,
    .stSelectbox [data-baseweb="popover"] ul[role="listbox"],
    .stSelectbox [data-baseweb="listbox"],
    .stSelectbox [data-baseweb="menu"],
    .stSelectbox [role="listbox"] {{
        background: var(--card-background) !important;
    }}
    
    /* Opciones individuales en el dropdown - Optimizado */
    .stSelectbox [role="option"] {{
        background: transparent !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        margin: 2px 4px !important;
        padding: 10px 12px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }}
    
    /* Contraste en fondos oscuros: si el menú conserva fondo negro, usar texto blanco */
    .stSelectbox [data-baseweb="popover"][style*="rgb(0, 0, 0)"] [role="option"],
    .stSelectbox [data-baseweb="popover"][style*="#000"] [role="option"],
    .stSelectbox [data-baseweb="listbox"][style*="rgb(0, 0, 0)"] [role="option"],
    .stSelectbox [data-baseweb="menu"][style*="rgb(0, 0, 0)"] [role="option"] {{
        color: #ffffff !important;
    }}
    
    /* Asegurar texto blanco en opción activa/seleccionada para visibilidad */
    .stSelectbox [role="option"][aria-selected="true"],
    .stSelectbox [role="option"][data-selected="true"] {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}
    
    .stSelectbox [role="option"]:hover {{
        background: var(--gradient-primary) !important;
        color: white !important;
        transform: translateX(2px) !important;
        box-shadow: 0 2px 8px rgba(46, 134, 171, 0.3) !important;
    }}
    
    /* Opción seleccionada - Optimizado */
    .stSelectbox [aria-selected="true"] {{
        background: var(--gradient-accent) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(241, 143, 1, 0.4) !important;
    }}
    
    /* Elementos SVG - Optimizado */
    svg {{
        background-color: var(--background-white) !important;
    }}
    
    /* Divs principales - Optimizado */
    .stApp > div, .main > div, .block-container {{
        background-color: var(--background-white) !important;
    }}
    
    /* Inputs de diferentes tipos - Optimizado */
    input[type="text"], input[type="number"], input[type="email"], input[type="password"] {{
        background-color: var(--background-white) !important;
        color: var(--text-primary) !important;
        border: 2px solid #e1e8ed !important;
    }}
    
    /* Mejoras para gráficos y visualizaciones - Optimizado */
    .stPlotlyChart {{
        background-color: var(--background-white) !important;
        border-radius: var(--border-radius);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        padding: 1.5rem !important;
        margin: 1rem 0;
        border: 2px solid var(--text-black) !important;
    }}
    
    /* Contenedor de gráficos - Optimizado */
    .js-plotly-plot {{
        background-color: var(--background-white) !important;
        border: 2px solid var(--text-black) !important;
        border-radius: var(--border-radius);
    }}
    
    /* SVG principal - Optimizado */
    .plotly svg {{
        background-color: var(--background-white) !important;
    }}
    
    /* Ejes y texto de gráficos - Optimizado */
    .plotly .xtick text, .plotly .ytick text,
    .stPlotlyChart .xtick text, .stPlotlyChart .ytick text,
    .plotly text[class*="xtick"], .plotly text[class*="ytick"] {{
        fill: var(--text-black) !important;
        color: var(--text-black) !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        font-family: 'Arial', sans-serif !important;
    }}
    
    /* Títulos de ejes - Optimizado */
    .plotly .xtitle, .plotly .ytitle {{
        fill: var(--text-black) !important;
        color: var(--text-black) !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        font-family: 'Arial', sans-serif !important;
    }}
    
    /* Líneas de ejes - Optimizado */
    .plotly .xaxis line, .plotly .yaxis line {{
        stroke: var(--text-black) !important;
        stroke-width: 2px !important;
    }}
    
    /* Barras de gráfico - Optimizado */
    .stBarChart > div {{
        background-color: var(--text-primary) !important;
        border: 3px solid #34495e !important;
        border-radius: var(--border-radius);
        padding: 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Texto en gráficos de barras - Optimizado */
    .stBarChart text {{
        fill: var(--background-white) !important;
        font-weight: 600 !important;
    }}
    
    /* Ejes de gráficos de barras - Optimizado */
    .stBarChart .tick text {{
        fill: var(--background-white) !important;
        font-weight: 500 !important;
    }}
    
    /* Líneas de ejes - Optimizado */
    .stBarChart .domain {{
        stroke: var(--background-white) !important;
        stroke-width: 2px !important;
    }}
    
    /* Líneas de cuadrícula - Optimizado */
    .plotly .gridlayer .crisp {{
        stroke: var(--text-black) !important;
        stroke-width: 2px !important;
        opacity: 1 !important;
    }}
    
    /* Cuadrícula principal - Optimizado */
    .plotly .xgrid, .plotly .ygrid {{
        stroke: var(--text-black) !important;
        stroke-width: 2px !important;
        opacity: 1 !important;
    }}
    
    /* Leyendas de gráficos - Optimizado */
    .plotly .legend {{
        background-color: var(--background-white) !important;
        border: 2px solid var(--text-black) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* Texto de leyendas - Optimizado */
    .plotly .legend text {{
        fill: var(--text-black) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    
    /* Tooltips - Optimizado */
    .plotly .hovertext {{
        background-color: var(--background-white) !important;
        color: var(--text-black) !important;
        border: 2px solid var(--text-black) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Elementos de barras - Optimizado */
    .plotly .bars path {{
        stroke: var(--text-black) !important;
        stroke-width: 1px !important;
    }}
    
    /* Texto en barras - Optimizado */
    .plotly .bartext {{
        fill: var(--text-black) !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8) !important;
    }}
    
    /* Textarea - Optimizado */
    textarea {{
        background-color: var(--background-white) !important;
        color: var(--text-primary) !important;
        border: 2px solid #e1e8ed !important;
    }}
    
    /* Contenedores de métricas - Optimizado */
    .metric-card {{
        background: var(--background-white) !important;
        border-radius: var(--border-radius);
        padding: 1.5rem !important;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        margin: 0.5rem 0;
        border: 2px solid var(--text-black) !important;
    }}
    
    /* Separación visual para gráficos - Optimizado */
    .stPlotlyChart::before {{
        content: "";
        display: block;
        height: 3px;
        background: linear-gradient(90deg, var(--text-black), #666666, var(--text-black));
        margin-bottom: 1rem;
        border-radius: 2px;
    }}
    
    /* Elementos de datos - Optimizado */
    .plotly .trace {{
        stroke-width: 2px !important;
    }}
    
    /* Marcadores de puntos - Optimizado */
    .plotly .scatterpts .point {{
        stroke: var(--text-black) !important;
        stroke-width: 2px !important;
    }}
    
    /* Separadores visuales - Optimizado */
    .stBarChart::after {{
        content: "";
        display: block;
        height: 2px;
        background: var(--text-black);
        margin-top: 1rem;
        opacity: 0.3;
    }}
    
    /* Área de fondo de gráficos - Optimizado */
    .plotly .subplot {{
        background-color: var(--background-white) !important;
        background-image: 
            linear-gradient(45deg, transparent 49%, rgba(0,0,0,0.02) 50%, transparent 51%),
            linear-gradient(-45deg, transparent 49%, rgba(0,0,0,0.02) 50%, transparent 51%);
        background-size: 20px 20px;
    }}
    
    /* Bordes adicionales para elementos SVG - Optimizado */
    .plotly .main-svg {{
        border: 1px solid var(--text-black) !important;
        border-radius: 4px !important;
    }}
    
    /* Resultados de búsqueda */
    .search-result {{
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-soft);
        border-left: 4px solid var(--accent-color);
        transition: all 0.3s ease;
    }}
    
    .search-result:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}
    
    /* Instrucciones destacadas */
    .instructions-box {{
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border: 2px solid var(--primary-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a365d !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Asegurar visibilidad en elementos específicos */
    .instructions-box *, .search-result *, .feature-card * {{
        color: #2c3e50 !important;
    }}
    
    /* Texto en botones debe mantenerse blanco */
    .stButton > button, .stButton > button * {{
        color: white !important;
    }}
    
    .category-badge {{
        background: var(--primary-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.2rem 0;
    }}
    
    .confidence-badge {{
        background: var(--success-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.2rem 0;
    }}
    
    /* Animaciones */
    .fade-in-up {{
        animation: fadeInUp 0.6s ease-out;
    }}
    
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 2rem;
        }}
        
        .main-container {{
            padding: 1rem;
            margin: 0.5rem;
        }}
        
        .feature-card {{
            padding: 1rem;
        }}
    }}
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def initialize_session_state() -> None:
    """Inicializa el estado de la sesión con valores por defecto."""
    # Inicializar valores básicos primero
    if 'voice_enabled' not in st.session_state:
        st.session_state.voice_enabled = True
    
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    if 'current_results' not in st.session_state:
        st.session_state.current_results = []
    
    # Inicializar el procesador de forma segura
    if 'processor' not in st.session_state:
        try:
            with st.spinner("Inicializando sistema de señas..."):
                st.session_state.processor = get_processor()
        except Exception as e:
            st.error(f"Error al inicializar el sistema: {e}")
            st.session_state.processor = None


def render_header() -> None:
    """Renderiza el encabezado principal de la aplicación."""
    header_html = f"""
    <div class="main-container fade-in-up">
        <h1 class="main-title">{APP_ICON} {APP_TITLE}</h1>
        <p class="subtitle">Traductor de Lengua de Señas</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def perform_search(query: str, search_type: str = "exact", language: str = "ecuatoriano") -> SearchResult:
    """
    Realiza una búsqueda y actualiza el estado de la sesión.
    
    Args:
        query: Término de búsqueda
        search_type: Tipo de búsqueda ('exact', 'fuzzy', 'auto')
        language: Idioma en el que buscar
    
    Returns:
        SearchResult con los resultados de búsqueda
    """
    if not query.strip():
        return SearchResult(query="", found=False)
    
    processor = st.session_state.processor
    
    # Verificar si es una palabra con versiones Costa/Sierra
    dual_version_words = ["mayo", "octubre", "noviembre"]
    query_lower = query.lower().strip()
    
    if query_lower in dual_version_words and language == "ecuatoriano":
        # Buscar ambas versiones (Costa y Sierra)
        costa_query = f"{query} (Costa)"
        sierra_query = f"{query} (Sierra)"
        
        costa_result = processor.search_sign(costa_query, include_similar=False, language=language)
        sierra_result = processor.search_sign(sierra_query, include_similar=False, language=language)
        
        # Crear un resultado combinado
        combined_result = SearchResult(query=query, found=False)
        
        if costa_result.found or sierra_result.found:
            combined_result.found = True
            # Agregar ambas versiones como coincidencias similares para mostrarlas
            if costa_result.found:
                combined_result.similar_matches.append((costa_result.exact_match, 1.0))
            if sierra_result.found:
                combined_result.similar_matches.append((sierra_result.exact_match, 1.0))
            
            # Usar la primera versión encontrada como coincidencia exacta
            if costa_result.found:
                combined_result.exact_match = costa_result.exact_match
            elif sierra_result.found:
                combined_result.exact_match = sierra_result.exact_match
        
        results = combined_result
    else:
        # Búsqueda normal
        if search_type == "exact":
            # Búsqueda exacta solamente
            results = processor.search_sign(query, include_similar=False, language=language)
        elif search_type == "fuzzy":
            # Búsqueda con similares
            results = processor.search_sign(query, include_similar=True, language=language)
        else:
            # Búsqueda automática: incluye similares por defecto
            results = processor.search_sign(query, include_similar=True, language=language)
    
    # Actualizar historial si es una nueva búsqueda
    if query not in st.session_state.search_history:
        st.session_state.search_history.append(query)
    
    # Actualizar resultados actuales
    st.session_state.current_results = results
    
    return results


def render_search_interface() -> None:
    """Renderiza la interfaz de búsqueda principal."""
    st.markdown("""
    <div class="feature-card fade-in-up">
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">🔍 Búsqueda de Señas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Pestañas de búsqueda
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Búsqueda Exacta", 
        "🔄 Búsqueda Inteligente", 
        "🎤 Búsqueda por Voz",
        "📊 Análisis Comparativo",
        "📷 Webcam"
    ])
    
    with tab1:
        _render_exact_search_tab()
    
    with tab2:
        _render_fuzzy_search_tab()
    
    with tab3:
        _render_voice_search_tab()
    
    with tab4:
        # Solo renderizar si el procesador está inicializado
        if hasattr(st.session_state, 'processor') and st.session_state.processor:
            _render_comparative_analysis_tab()
        else:
            st.error("Sistema no inicializado correctamente. Por favor, recarga la página.")

    with tab5:
        _render_webcam_tab()


def _render_webcam_tab() -> None:
    """Renderiza la pestaña de reconocimiento por webcam."""
    # Encabezado con estilo
    st.markdown("""
    <div class="feature-card fade-in-up">
        <h2 style="color: var(--primary-color); margin-bottom: 0.5rem;">📷 Reconocimiento en Tiempo Real</h2>
        <p style="color: var(--text-secondary);">Utiliza tu cámara web para traducir señas instantáneamente.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instructions-box" style="margin-bottom: 2rem;">
        <span style="font-size: 1.2rem;">💡</span> <strong>Consejos:</strong>
        <ul style="margin-bottom: 0;">
            <li>Asegúrate de cerrar otras aplicaciones que usen la cámara (como <strong>Google Meet, Zoom, Teams</strong>).</li>
            <li>Ten buena iluminación y muestra tus manos claramente.</li>
            <li>Si no carga, prueba cambiando el índice de la cámara o recargando la página.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown("### 🎛️ Controles")
        
        # Panel de control estilizado
        st.markdown("""
        <div style="background: var(--card-background); padding: 1.5rem; border-radius: 12px; box-shadow: var(--shadow-soft); border: 1px solid rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        
        # Selector de cámara
        camera_index = st.selectbox(
            "Seleccionar Dispositivo de Cámara:",
            options=[0, 1, 2],
            format_func=lambda x: f"Cámara {x}",
            key="camera_selector"
        )
        
        run_camera = st.toggle('🔴 Activar Cámara', key="run_webcam_toggle")
        
        if st.button("🔄 Recargar Modelo", use_container_width=True):
             if 'webcam_predictor' in st.session_state:
                 del st.session_state.webcam_predictor
             st.toast("Modelo recargado correctamente", icon="✅")
             
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Estado del sistema
        status_placeholder = st.empty()
             
    with col2:
        st.markdown("### 👁️ Vista Previa")
        # Contenedor para el video con borde y sombra
        video_container = st.container()
        with video_container:
            frame_placeholder = st.empty()
    
    if run_camera:
        # Inicializar predictor si no existe
        if 'webcam_predictor' not in st.session_state:
            with st.spinner("Cargando modelo de inteligencia artificial..."):
                try:
                    st.session_state.webcam_predictor = SignLanguagePredictor()
                except Exception as e:
                    st.error(f"Error cargando el modelo: {e}")
                    return

        # Debug info
        # st.write(f"Intentando abrir cámara con índice: {camera_index}")
        
        # Captura de video
        # Usar el índice seleccionado
        cap = None
        try:
            # Intento 1: DirectShow (Rápido en Windows)
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            
            if not cap or not cap.isOpened():
                # Intento 2: Backend por defecto (MSMF en Windows)
                cap = cv2.VideoCapture(camera_index)
                
            if not cap or not cap.isOpened():
                 st.error(f"⚠️ No se pudo acceder a la Cámara {camera_index}. Intenta seleccionar otro índice.")
                 return
                 
        except Exception as e:
            st.error(f"Excepción al abrir cámara: {e}")
            return
            
        status_placeholder.markdown("""
            <div style="background: #e3f2fd; color: #0d47a1; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3;">
                <strong>Estado:</strong> 🟢 Cámara activa
            </div>
        """, unsafe_allow_html=True)
        
        try:
            empty_reads = 0
            while run_camera:
                ret, frame = cap.read()
                
                if not ret:
                    empty_reads += 1
                    if empty_reads > 10:
                        st.error("No se recibe señal de video. Verifica que la cámara no esté siendo usada por otra aplicación.")
                        break
                    time.sleep(0.1)
                    continue
                
                empty_reads = 0 # Reset contador si leemos bien
                
                # Procesar frame
                annotated_frame, prediction, num_hands = st.session_state.webcam_predictor.process_frame(frame)
                
                # Convertir BGR a RGB
                frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                
                # Mostrar en Streamlit con estilo
                frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
                # Mostrar resultado
                if prediction:
                    status_placeholder.markdown(f"""
                    <div class="search-result fade-in-up" style="text-align: center; border-left: 5px solid var(--success-color);">
                        <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">TRADUCCIÓN DETECTADA</div>
                        <h2 style="color: var(--primary-color); font-size: 2.5rem; margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                            🤟 {prediction}
                        </h2>
                        <div style="margin-top: 1rem;">
                            <span class="category-badge" style="background: var(--accent-color);">Manos: {num_hands}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    status_placeholder.markdown(f"""
                    <div style="background: var(--card-background); padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px dashed #ccc;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">✋</div>
                        <h4 style="color: var(--text-secondary); margin: 0;">Esperando seña...</h4>
                        <p style="font-size: 0.8rem; color: #666;">Manos visibles: {num_hands}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error durante la ejecución: {e}")
        finally:
            cap.release()
            status_placeholder.markdown("""
                <div style="background: #fff3e0; color: #e65100; padding: 1rem; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <strong>Estado:</strong> ⏸️ Cámara detenida
                </div>
            """, unsafe_allow_html=True)


def _render_exact_search_tab() -> None:
    """Renderiza la pestaña de búsqueda exacta."""
    st.markdown("Busca una seña específica por su nombre exacto:")
    
    # Selector de idioma
    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_input(
            "Ingresa la palabra a buscar:",
            placeholder="Ejemplo: hola, gracias, por favor...",
            key="exact_search"
        )
    
    with col2:
        language = st.selectbox(
            "Idioma de señas:",
            options=["ecuatoriano", "chileno", "mexicano"],
            index=0,
            key="language_selector"
        )
    
    col3, col4, col5, col6 = st.columns([1, 1, 1, 1])
    with col3:
        if st.button("🔍 Buscar", key="exact_btn"):
            if query:
                results = perform_search(query, "exact", language)
                _play_search_results_audio(results, language)
    
    with col4:
        if st.button("🧹 Limpiar", key="exact_clear_btn"):
            # Limpiar resultados y mostrar mensaje
            st.session_state.current_results = None
            st.success("Búsqueda limpiada")
            st.rerun()
    
    with col5:
        if st.button("⏹️ Detener Audio", key="exact_stop_btn"):
            if hasattr(st.session_state, 'processor') and st.session_state.processor:
                try:
                    st.session_state.processor.speech_engine.stop_speech()
                    st.info("Audio detenido")
                except Exception as e:
                    print(f"Error deteniendo audio: {e}")


def _render_fuzzy_search_tab() -> None:
    """Renderiza la pestaña de búsqueda inteligente."""
    st.markdown("Encuentra señas similares aunque no escribas la palabra exacta:")
    
    # Selector de idioma
    col1, col2 = st.columns([2, 1])
    with col2:
        language = st.selectbox(
            "Idioma:",
            options=["ecuatoriano", "chileno", "mexicano"],
            index=0,
            key="fuzzy_language"
        )
    
    with col1:
        query = st.text_input(
            "Buscar seña (inteligente):",
            placeholder="Ej: ola, grcias, adios...",
            key="fuzzy_query"
        )
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🔍 Buscar", key="fuzzy_btn"):
            if query:
                results = perform_search(query, "fuzzy", language)
                _play_search_results_audio(results, language)
    
    with col2:
        if st.button("🧹 Limpiar", key="fuzzy_clear_btn"):
            # Limpiar resultados y mostrar mensaje
            st.session_state.current_results = None
            st.success("Búsqueda limpiada")
            st.rerun()
    
    with col3:
        if st.button("⏹️ Detener Audio", key="fuzzy_stop_btn"):
            if hasattr(st.session_state, 'processor') and st.session_state.processor:
                try:
                    st.session_state.processor.speech_engine.stop_speech()
                    st.info("Audio detenido")
                except Exception as e:
                    print(f"Error deteniendo audio: {e}")


def _render_voice_search_tab() -> None:
    """Renderiza la pestaña de búsqueda por voz."""
    st.markdown("Usa tu voz para buscar señas:")
    
    # Selector de idioma
    col1, col2 = st.columns([2, 1])
    with col2:
        language = st.selectbox(
            "Idioma:",
            options=["ecuatoriano", "chileno", "mexicano"],
            index=0,
            key="voice_language"
        )
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.info("Haz clic en el botón y habla claramente la palabra que deseas buscar.")
    
    with col2:
        if st.button("🎤 Escuchar", key="voice_btn"):
            _handle_voice_search(language)
    
    with col3:
        if st.button("🧹 Limpiar", key="voice_clear_btn"):
            # Limpiar resultados de búsqueda por voz
            st.session_state.current_results = None
            st.success("Búsqueda limpiada")
            st.rerun()
    
    with col4:
        if st.button("⏹️ Detener Audio", key="voice_stop_btn"):
            if hasattr(st.session_state, 'processor') and st.session_state.processor:
                try:
                    st.session_state.processor.speech_engine.stop_speech()
                    st.info("Audio detenido")
                except Exception as e:
                    print(f"Error deteniendo audio: {e}")


def _handle_voice_search(language: str = "ecuatoriano") -> None:
    """Maneja la búsqueda por reconocimiento de voz."""
    with st.spinner("Escuchando... Habla ahora"):
        try:
            voice_engine = get_voice_recognition()
            recognized_text = voice_engine.record_and_transcribe()
            
            if recognized_text:
                # Limpiar y normalizar el texto reconocido (ahora viene mejor procesado)
                cleaned_text = recognized_text.strip()
                st.success(f"Reconocido: {recognized_text}")
                
                # Intentar primero búsqueda exacta
                results = perform_search(cleaned_text, "exact", language)
                if not results.found:
                    # Si no se encuentra exacta, intentar con fuzzy para obtener sugerencias
                    results = perform_search(cleaned_text, "fuzzy", language)
                    if results.found:
                        st.info(f"Búsqueda aproximada encontrada para: {cleaned_text}")
                    else:
                        # Asegurar que se incluyan sugerencias incluso si no hay coincidencias exactas
                        st.info(f"No se encontraron coincidencias exactas para: {cleaned_text}")
                
                # Actualizar los resultados en la sesión para mostrar sugerencias
                st.session_state.current_results = results
                _play_search_results_audio(results, language)
            else:
                st.warning("No se pudo reconocer el audio. Intenta de nuevo.")
        except Exception as e:
            st.error(f"Error en reconocimiento de voz: {str(e)}")


def _play_search_results_audio(results: SearchResult, language: str = "ecuatoriano") -> None:
    """
    Reproduce audio de los resultados de búsqueda en segundo plano.
    
    Args:
        results: Resultado de búsqueda (SearchResult)
        language: Idioma de la búsqueda
    """
    if not results:
        return
        
    if not st.session_state.voice_enabled:
        return
        
    # Verificar que el processor esté inicializado
    if not hasattr(st.session_state, 'processor') or not st.session_state.processor:
        st.error("Procesador no inicializado")
        return
    
    # Obtener referencia al speech_engine ANTES del threading
    speech_engine = st.session_state.processor.speech_engine
    
    try:
        if results.found and results.exact_match:
            # Reproducir resultado exacto
            def play_audio():
                try:
                    speech_engine.speak_sign_instruction(
                        results.exact_match.word, 
                        results.exact_match.instructions,
                        language
                    )
                except Exception as e:
                    print(f"Error reproduciendo audio: {e}")
            
            threading.Thread(target=play_audio, daemon=True).start()
            
        elif results.similar_matches:
            # Reproducir mejor coincidencia similar
            best_match, similarity = results.similar_matches[0]
            
            def play_similar_audio():
                try:
                    # Mapeo de idiomas a países
                    language_country_map = {
                        "ecuatoriano": "Ecuador",
                        "chileno": "Chile", 
                        "mexicano": "México"
                    }
                    
                    country = language_country_map.get(language, "Ecuador")
                    
                    suggestion_text = (
                        f"No encontré exactamente '{results.query}' en lengua de señas de {country}, "
                        f"pero encontré '{best_match.word}' que es similar. "
                        f"La palabra '{best_match.word}' en lengua de señas de {country} se hace así: {best_match.instructions}"
                    )
                    speech_engine.speak_text(suggestion_text)
                except Exception as e:
                    print(f"Error reproduciendo audio similar: {e}")
            
            threading.Thread(target=play_similar_audio, daemon=True).start()
            
        else:
            # No se encontraron resultados
            def play_no_results():
                try:
                    no_results_text = f"No se encontraron resultados para '{results.query}'"
                    speech_engine.speak_text(no_results_text)
                except Exception as e:
                    print(f"Error reproduciendo mensaje de no resultados: {e}")
            
            threading.Thread(target=play_no_results, daemon=True).start()
            
    except Exception as e:
        st.error(f"Error en reproducción de audio: {str(e)}")
        print(f"Error detallado en _play_search_results_audio: {e}")


def render_results() -> None:
    """Renderiza los resultados de búsqueda."""
    if not st.session_state.current_results:
        return
    
    st.markdown("""
    <div class="feature-card fade-in-up">
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">📋 Resultados de Búsqueda</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # current_results ahora es un SearchResult, no una lista
    result = st.session_state.current_results
    _render_single_result(result, 0)


def _render_single_result(result: SearchResult, index: int) -> None:
    """
    Renderiza un resultado individual de búsqueda.
    
    Args:
        result: Resultado de búsqueda
        index: Índice del resultado
    """
    if not result.found:
        # Mostrar mensaje de no encontrado
        st.warning(f"No se encontraron resultados para '{result.query}'")
        
        # Mostrar sugerencias si están disponibles
        if result.similar_matches:
            st.info("💡 **Sugerencias de palabras similares:**")
            
            # Mostrar hasta 3 sugerencias principales
            for i, (similar_sign, similarity) in enumerate(result.similar_matches[:3]):
                suggestion_html = f"""
                <div class="suggestion-result" style="
                    background: linear-gradient(45deg, #f8f9fa, #e9ecef); 
                    border-left: 4px solid var(--accent-color);
                    padding: 0.8rem; 
                    margin: 0.5rem 0; 
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: var(--primary-color); font-size: 1.1rem;">
                                🤟 {similar_sign.word}
                            </strong>
                            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.3rem;">
                                {similar_sign.instructions[:100]}{'...' if len(similar_sign.instructions) > 100 else ''}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="
                                background: var(--accent-color); 
                                color: white; 
                                padding: 0.2rem 0.5rem; 
                                border-radius: 12px; 
                                font-size: 0.8rem;
                                font-weight: bold;
                            ">
                                {similarity:.0%} similar
                            </span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(suggestion_html, unsafe_allow_html=True)
                
                # Botón para usar esta sugerencia
                if st.button(f"🔍 Buscar '{similar_sign.word}'", key=f"suggestion_{index}_{i}"):
                    # Realizar nueva búsqueda con la sugerencia
                    new_results = perform_search(similar_sign.word, "exact")
                    st.session_state.current_results = new_results
                    st.rerun()
        
        return
    
    # Verificar si es una búsqueda de versiones duales (Costa y Sierra)
    dual_version_words = ["mayo", "octubre", "noviembre"]
    query_lower = result.query.lower().strip()
    
    if query_lower in dual_version_words and len(result.similar_matches) >= 2:
        # Mostrar ambas versiones (Costa y Sierra) de manera especial
        st.markdown(f"""
        <div class="search-result fade-in-up">
            <div style="background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)); 
                        color: white; padding: 1rem; border-radius: var(--border-radius); 
                        margin-bottom: 1rem; text-align: center; box-shadow: var(--shadow-soft);">
                <h2 style="margin: 0; font-size: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🤟 {result.query.title()} - Versiones Regionales
                </h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar cada versión en su propia tarjeta
        for i, (version_sign, similarity) in enumerate(result.similar_matches):
            # Determinar si es Costa o Sierra
            region = "🏖️ Costa" if "(Costa)" in version_sign.word else "🏔️ Sierra"
            region_color = "#2E86AB" if "Costa" in version_sign.word else "#A23B72"
            
            version_html = f"""
            <div class="search-result" style="margin: 1rem 0; border-left: 4px solid {region_color};">
                <div style="background: linear-gradient(45deg, {region_color}, #667eea); 
                            color: white; padding: 0.8rem; border-radius: var(--border-radius); 
                            margin-bottom: 1rem; text-align: center; box-shadow: var(--shadow-soft);">
                    <h3 style="margin: 0; font-size: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        {region} - {version_sign.word}
                    </h3>
                </div>
                <div class="instructions-box">
                    <strong>Instrucciones:</strong> {version_sign.instructions}
                </div>
                <div style="margin: 1rem 0;">
                    <span class="category-badge">Categoría: {version_sign.category}</span>
                </div>
            </div>
            """
            st.markdown(version_html, unsafe_allow_html=True)
            
            # Botones para reproducir y detener audio de cada versión
            if st.session_state.voice_enabled:
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button(f"🔊 Reproducir {region}", key=f"speak_version_{index}_{i}"):
                        # Verificar que el processor esté inicializado
                        if hasattr(st.session_state, 'processor') and st.session_state.processor:
                            # Obtener referencia al speech_engine ANTES del threading
                            speech_engine = st.session_state.processor.speech_engine
                            
                            def play_version_instruction():
                                try:
                                    speech_engine.speak_sign_instruction(
                                        version_sign.word, version_sign.instructions
                                    )
                                except Exception as e:
                                    print(f"Error reproduciendo instrucción: {e}")
                            
                            threading.Thread(target=play_version_instruction, daemon=True).start()
                            st.success(f"Reproduciendo versión {region}...")
                
                with col2:
                    if st.button(f"⏹️ Detener", key=f"stop_version_{index}_{i}"):
                        # Verificar que el processor esté inicializado
                        if hasattr(st.session_state, 'processor') and st.session_state.processor:
                            try:
                                st.session_state.processor.speech_engine.stop_speech()
                                st.info("Audio detenido")
                            except Exception as e:
                                print(f"Error deteniendo audio: {e}")
        
        return
    
    # Renderizado normal para otros resultados
    # Obtener la mejor coincidencia
    best_match = result.get_best_match()
    if not best_match:
        st.warning("No hay coincidencias disponibles")
        return
    
    confidence = result.get_confidence_score()
    
    result_html = f"""
    <div class="search-result fade-in-up">
        <div style="background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)); 
                    color: white; padding: 1rem; border-radius: var(--border-radius); 
                    margin-bottom: 1rem; text-align: center; box-shadow: var(--shadow-soft);">
            <h2 style="margin: 0; font-size: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🤟 {best_match.word}
            </h2>
        </div>
        <div class="instructions-box">
            <strong>Instrucciones:</strong> {best_match.instructions}
        </div>
        <div style="margin: 1rem 0;">
            <span class="category-badge">Categoría: {best_match.category}</span>
            <span class="confidence-badge">Coincidencia: {confidence:.1%}</span>
        </div>
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)
    
    # Botones para reproducir y detener audio
    if st.session_state.voice_enabled:
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button(f"🔊 Reproducir", key=f"speak_{index}"):
                # Verificar que el processor esté inicializado
                if hasattr(st.session_state, 'processor') and st.session_state.processor:
                    # Obtener referencia al speech_engine ANTES del threading
                    speech_engine = st.session_state.processor.speech_engine
                    
                    def play_instruction():
                        try:
                            speech_engine.speak_sign_instruction(
                                best_match.word, best_match.instructions
                            )
                        except Exception as e:
                            print(f"Error reproduciendo instrucción: {e}")
                    
                    threading.Thread(target=play_instruction, daemon=True).start()
                    st.success("Reproduciendo...")
        
        with col2:
            if st.button(f"⏹️ Detener", key=f"stop_{index}"):
                # Verificar que el processor esté inicializado
                if hasattr(st.session_state, 'processor') and st.session_state.processor:
                    try:
                        st.session_state.processor.speech_engine.stop_speech()
                        st.info("Audio detenido")
                    except Exception as e:
                        print(f"Error deteniendo audio: {e}")


def render_random_signs() -> None:
    """Renderiza sección de señas aleatorias para exploración."""
    st.markdown("""
    <div class="feature-card fade-in-up">
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">🎲 Explorar Señas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎲 Seña Aleatoria", key="random_sign"):
            _show_random_sign()
    
    with col2:
        if st.button("📚 5 Señas Aleatorias", key="random_signs"):
            _show_multiple_random_signs()


def _show_random_sign() -> None:
    """Muestra una seña aleatoria."""
    random_signs = st.session_state.processor.get_random_signs(1)
    if random_signs:
        sign = random_signs[0]
        result_html = f"""
        <div class="search-result">
            <div style="background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)); 
                        color: white; padding: 0.8rem; border-radius: var(--border-radius); 
                        margin-bottom: 1rem; text-align: center; box-shadow: var(--shadow-soft);">
                <h2 style="margin: 0; font-size: 1.8rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🤟 {sign.word}
                </h2>
            </div>
            <div class="instructions-box">
                <strong>Instrucciones:</strong> {sign.instructions}
            </div>
            <div style="margin: 1rem 0;">
                <span class="category-badge">Categoría: {sign.category}</span>
            </div>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)
        
        if st.session_state.voice_enabled:
            # Obtener referencia al speech_engine ANTES del threading
            speech_engine = st.session_state.processor.speech_engine
            
            def play_random_sign():
                try:
                    speech_engine.speak_sign_instruction(
                        sign.word, sign.instructions
                    )
                except Exception as e:
                    print(f"Error reproduciendo seña aleatoria: {e}")
            
            threading.Thread(target=play_random_sign, daemon=True).start()


def _show_multiple_random_signs() -> None:
    """Muestra múltiples señas aleatorias."""
    random_signs = st.session_state.processor.get_random_signs(5)
    for sign in random_signs:
        result_html = f"""
        <div class="search-result">
            <div style="background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)); 
                        color: white; padding: 0.6rem; border-radius: var(--border-radius); 
                        margin-bottom: 0.8rem; text-align: center; box-shadow: var(--shadow-soft);">
                <h3 style="margin: 0; font-size: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🤟 {sign.word}
                </h3>
            </div>
            <div class="instructions-box">
                {sign.instructions}
            </div>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)


def render_footer() -> None:
    """Renderiza el pie de página de la aplicación."""
    footer_html = """
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; color: var(--text-secondary);">
        <p>Traductor de Lengua de Señas</p>
        <p>Desarrollado con ❤️ para la comunidad Sorda y Muda</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


def _render_comparative_analysis_tab() -> None:
    """Renderiza la pestaña de análisis comparativo entre idiomas."""
    st.markdown("Análisis estadístico comparativo entre diferentes lenguajes de señas:")
    
    # Verificar que el procesador esté inicializado
    if not hasattr(st.session_state, 'processor') or not st.session_state.processor:
        st.error("Sistema no inicializado correctamente. Por favor, recarga la página.")
        return
    
    # Obtener la base de datos a través del procesador
    database = st.session_state.processor.database
    
    # Obtener el analizador comparativo
    analyzer = get_comparative_analyzer(database)
    
    # Selector de tipo de análisis
    analysis_type = st.selectbox(
        "Tipo de análisis:",
        options=[
            "Estadísticas Descriptivas",
            "Palabras Comunes"
        ],
        key="analysis_type"
    )
    
    if st.button("🔬 Realizar Análisis", key="run_analysis"):
        with st.spinner("Realizando análisis..."):
            try:
                if analysis_type == "Estadísticas Descriptivas":
                    # Generar estadísticas descriptivas
                    stats_table = analyzer.create_statistical_summary_table()
                    
                    st.subheader("📊 Estadísticas No Paramétricas por Idioma")
                    st.write("Análisis estadístico enfocado en la complejidad de las instrucciones de señas:")
                    
                    if not stats_table.empty:
                        st.dataframe(stats_table, use_container_width=True)
                        
                        # Mostrar gráfico de barras para cantidad de señas
                        if 'Cantidad' in stats_table.columns:
                            st.subheader("📈 Cantidad de Señas Comunes por Idioma")
                            st.bar_chart(stats_table['Cantidad'])
                        
                        # Mostrar comparación de medianas
                        if 'Mediana' in stats_table.columns:
                            st.subheader("📊 Comparación de Complejidad (Mediana de longitud)")
                            st.bar_chart(stats_table['Mediana'])
                            
                        # Mostrar análisis de complejidad
                        if 'Complejidad Promedio' in stats_table.columns:
                            st.subheader("🎯 Clasificación de Complejidad")
                            complexity_counts = stats_table['Complejidad Promedio'].value_counts()
                            st.bar_chart(complexity_counts)
                    else:
                        st.info("No hay datos suficientes para generar estadísticas descriptivas.")
                
                elif analysis_type == "Palabras Comunes":
                    # Obtener palabras comunes
                    common_words = database.get_common_words()
                    
                    st.subheader("🔗 Palabras Comunes Entre Idiomas")
                    st.write(f"Se encontraron **{len(common_words)}** palabras presentes en todos los idiomas:")
                    
                    if common_words:
                        # Mostrar palabras en columnas
                        cols = st.columns(3)
                        for i, word in enumerate(common_words):
                            with cols[i % 3]:
                                st.write(f"• {word}")
                    else:
                        st.info("No se encontraron palabras comunes entre todos los idiomas.")
                
            except Exception as e:
                st.error(f"Error al realizar el análisis: {str(e)}")
                st.write("Por favor, verifica que la base de datos esté correctamente cargada.")


def main() -> None:
    """Función principal de la aplicación."""
    # Cargar CSS personalizado
    load_custom_css()
    
    # Inicializar estado de sesión
    initialize_session_state()
    
    # Renderizar componentes principales
    render_header()
    # render_sidebar() eliminado
    render_search_interface()
    render_results()
    # render_random_signs() eliminado
    render_footer()


if __name__ == "__main__":
    main()