import streamlit as st
import pandas as pd
import plotly.express as px

def render_geo_analytics():  # <-- CAMBIAR NOMBRE DE FUNCIÓN
    """
    Muestra el dashboard de análisis geográfico
    """
    st.title("🌍 Dashboard de Análisis Geográfico")
    
    # Primero verificar si hay datos cargados
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ Primero carga los datos en la sección 'Análisis de Clientes'")
        return
    
    df = st.session_state.df
    
    # Seleccionar nivel de análisis
    analysis_level = st.radio(
        "Nivel de análisis geográfico",
        ["Región", "País", "Estado", "Ciudad"],
        horizontal=True
    )
    
    if analysis_level == "Región":
        show_region_analysis(df)
    elif analysis_level == "País":
        show_country_analysis(df)
    elif analysis_level == "Estado":
        show_state_analysis(df)
    elif analysis_level == "Ciudad":
        show_city_analysis(df)

def show_region_analysis(df):
    """Análisis por región"""
    st.header("Análisis por Región")
    
    # Verificar columnas necesarias
    required_cols = ['Order Region', 'Latitude', 'Longitude', 'Sales']
    if not all(col in df.columns for col in required_cols):
        st.error("Faltan columnas necesarias para el análisis regional")
        st.write("Columnas disponibles:", list(df.columns)[:20])
        return
    
    # Preparar datos
    df_clean = df.dropna(subset=required_cols).copy()
    
    # Estadísticas por región
    region_stats = df_clean.groupby('Order Region').agg({
        'Sales': ['sum', 'mean', 'count'],
        'Order Item Discount Rate': 'mean',
        'Order Item Quantity': 'mean'
    }).round(2)
    
    region_stats.columns = ['Ventas Totales', 'Ventas Promedio', 'Pedidos', 
                           'Descuento Promedio', 'Cantidad Promedio']
    
    st.subheader("Estadísticas por Región")
    st.dataframe(region_stats.sort_values('Ventas Totales', ascending=False))
    
    # Mapa de calor geográfico
    st.subheader("Mapa de Ventas por Región")
    
    # Agregar coordenadas aproximadas si no existen
    if 'Latitude' in df_clean.columns and 'Longitude' in df_clean.columns:
        region_coords = df_clean.groupby('Order Region')[['Latitude', 'Longitude']].mean()
        region_sales = df_clean.groupby('Order Region')['Sales'].sum()
        
        # Crear DataFrame para el mapa
        map_data = pd.DataFrame({
            'region': region_coords.index,
            'lat': region_coords['Latitude'],
            'lon': region_coords['Longitude'],
            'sales': region_sales
        }).dropna()
        
        if not map_data.empty:
            fig = px.scatter_geo(
                map_data,
                lat='lat',
                lon='lon',
                size='sales',
                hover_name='region',
                title="Distribución de Ventas por Región",
                projection="natural earth",
                size_max=50
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos geográficos suficientes para mostrar el mapa")

def show_country_analysis(df):
    """Análisis por país"""
    st.header("Análisis por País")
    
    if 'Customer Country' not in df.columns:
        st.error("No hay datos de países disponibles")
        return
    
    # Estadísticas por país
    country_stats = df.groupby('Customer Country').agg({
        'Sales': ['sum', 'mean', 'count'],
        'Order Item Discount Rate': 'mean',
        'Order Item Quantity': 'mean'
    }).round(2)
    
    country_stats.columns = ['Ventas Totales', 'Ventas Promedio', 'Pedidos', 
                            'Descuento Promedio', 'Cantidad Promedio']
    
    st.subheader("Estadísticas por País")
    st.dataframe(country_stats.sort_values('Ventas Totales', ascending=False))
    
    # Gráfico de barras
    top_countries = country_stats.nlargest(10, 'Ventas Totales')
    
    fig = px.bar(
        top_countries.reset_index(),
        x='Customer Country',
        y='Ventas Totales',
        title='Top 10 Países por Ventas',
        color='Ventas Totales',
        color_continuous_scale='viridis'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_state_analysis(df):
    """Análisis por estado/provincia"""
    st.header("Análisis por Estado/Provincia")
    
    if 'Customer State' not in df.columns:
        st.error("No hay datos de estados disponibles")
        return
    
    # Estadísticas por estado
    state_stats = df.groupby('Customer State').agg({
        'Sales': ['sum', 'mean', 'count'],
        'Order Item Discount Rate': 'mean',
        'Order Item Quantity': 'mean'
    }).round(2)
    
    state_stats.columns = ['Ventas Totales', 'Ventas Promedio', 'Pedidos', 
                          'Descuento Promedio', 'Cantidad Promedio']
    
    st.subheader("Estadísticas por Estado")
    st.dataframe(state_stats.sort_values('Ventas Totales', ascending=False))
    
    # Mostrar top 10 estados
    top_states = state_stats.nlargest(10, 'Ventas Totales').reset_index()
    
    fig = px.bar(
        top_states,
        x='Customer State',
        y='Ventas Totales',
        title='Top 10 Estados por Ventas',
        color='Ventas Totales',
        color_continuous_scale='plasma'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_city_analysis(df):
    """Análisis por ciudad"""
    st.header("Análisis por Ciudad")
    
    # Usar Order City o Customer City
    city_col = 'Order City' if 'Order City' in df.columns else 'Customer City'
    
    if city_col not in df.columns:
        st.error("No hay datos de ciudades disponibles")
        return
    
    # Estadísticas por ciudad
    city_stats = df.groupby(city_col).agg({
        'Sales': ['sum', 'mean', 'count'],
        'Order Item Discount Rate': 'mean',
        'Order Item Quantity': 'mean'
    }).round(2)
    
    city_stats.columns = ['Ventas Totales', 'Ventas Promedio', 'Pedidos', 
                         'Descuento Promedio', 'Cantidad Promedio']
    
    st.subheader("Estadísticas por Ciudad")
    
    # Mostrar top 15 ciudades
    top_cities = city_stats.nlargest(15, 'Ventas Totales').reset_index()
    st.dataframe(top_cities)
    
    # Gráfico
    fig = px.bar(
        top_cities.head(10),
        x=city_col,
        y='Ventas Totales',
        title='Top 10 Ciudades por Ventas',
        color='Ventas Totales',
        color_continuous_scale='rainbow'
    )
    
    st.plotly_chart(fig, use_container_width=True)