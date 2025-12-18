# components/product_analytics.py - VERSIÓN SIN ProductAnalyzer
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def render_product_analytics():
    """Renderiza el análisis de productos - Versión simplificada"""
    
    st.title("📦 Análisis de Productos")
    
    # Verificar si hay datos cargados
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ Primero carga los datos en 'Análisis de Clientes'")
        return
    
    df = st.session_state.df
    
    # Mostrar columnas disponibles
    with st.expander("🔍 Columnas disponibles"):
        st.write(f"Total columnas: {len(df.columns)}")
        st.write("Primeras 20 columnas:", list(df.columns)[:20])
    
    # Detectar columnas automáticamente
    detected = detect_columns(df)
    
    # Menú de análisis
    st.sidebar.header("⚙️ Configuración")
    
    analysis_type = st.sidebar.radio(
        "Tipo de análisis:",
        ["Resumen", "Por Producto", "Por Categoría", "Tendencias"],
        index=0
    )
    
    # Mostrar análisis según selección
    if analysis_type == "Resumen":
        show_summary(df, detected)
    elif analysis_type == "Por Producto":
        show_product_analysis(df, detected)
    elif analysis_type == "Por Categoría":
        show_category_analysis(df, detected)
    elif analysis_type == "Tendencias":
        show_trends_analysis(df, detected)

def detect_columns(df):
    """Detecta columnas relevantes"""
    detected = {}
    
    # Buscar patrones
    for col in df.columns:
        col_lower = str(col).lower()
        
        if 'product' in col_lower and 'name' in col_lower:
            detected['product'] = col
        elif 'categor' in col_lower:
            detected['category'] = col
        elif 'sales' in col_lower:
            detected['sales'] = col
        elif 'quant' in col_lower:
            detected['quantity'] = col
        elif 'price' in col_lower:
            detected['price'] = col
        elif 'date' in col_lower:
            detected['date'] = col
    
    return detected

def show_summary(df, detected):
    """Muestra resumen general"""
    st.header("📊 Resumen General")
    
    # Métricas básicas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'product' in detected:
            unique_products = df[detected['product']].nunique()
            st.metric("Productos Únicos", f"{unique_products:,}")
    
    with col2:
        if 'sales' in detected:
            total_sales = df[detected['sales']].sum()
            st.metric("Ventas Totales", f"${total_sales:,.2f}")
    
    with col3:
        if 'quantity' in detected:
            total_qty = df[detected['quantity']].sum()
            st.metric("Cantidad Total", f"{total_qty:,}")
    
    with col4:
        if 'category' in detected:
            unique_cats = df[detected['category']].nunique()
            st.metric("Categorías", f"{unique_cats:,}")
    
    # Top productos si tenemos datos
    if 'product' in detected and 'sales' in detected:
        st.subheader("🏆 Top 10 Productos")
        
        top_products = df.groupby(detected['product'])[detected['sales']].sum()
        top_products = top_products.sort_values(ascending=False).head(10)
        
        # Mostrar como tabla
        st.dataframe(top_products.reset_index().rename(
            columns={detected['product']: 'Producto', detected['sales']: 'Ventas'}
        ), use_container_width=True)
        
        # Gráfico
        fig = px.bar(
            top_products.reset_index(),
            x=detected['product'],
            y=detected['sales'],
            title="Top 10 Productos por Ventas"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_product_analysis(df, detected):
    """Análisis por producto"""
    st.header("📦 Análisis por Producto")
    
    if 'product' not in detected:
        st.error("No se encontró columna de productos")
        return
    
    # Configuración
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Número de productos", 5, 50, 20)
    with col2:
        metric = st.selectbox("Métrica", ["Ventas", "Cantidad", "Frecuencia"])
    
    # Agrupar por producto
    group_cols = [detected['product']]
    agg_dict = {}
    
    if 'sales' in detected and metric == "Ventas":
        agg_dict[detected['sales']] = 'sum'
    elif 'quantity' in detected and metric == "Cantidad":
        agg_dict[detected['quantity']] = 'sum'
    else:
        # Frecuencia por defecto
        agg_dict[detected['product']] = 'size'
    
    if agg_dict:
        result = df.groupby(group_cols).agg(agg_dict).reset_index()
        result = result.sort_values(result.columns[-1], ascending=False).head(top_n)
        
        st.dataframe(result, use_container_width=True)

def show_category_analysis(df, detected):
    """Análisis por categoría"""
    st.header("📂 Análisis por Categoría")
    
    if 'category' not in detected:
        st.error("No se encontró columna de categoría")
        return
    
    if 'sales' not in detected:
        st.error("No se encontró columna de ventas")
        return
    
    # Agrupar por categoría
    result = df.groupby(detected['category'])[detected['sales']].sum()
    result = result.sort_values(ascending=False)
    
    # Mostrar tabla
    st.dataframe(result.reset_index().rename(
        columns={detected['category']: 'Categoría', detected['sales']: 'Ventas'}
    ), use_container_width=True)
    
    # Gráfico
    fig = px.pie(
        result.reset_index(),
        values=detected['sales'],
        names=detected['category'],
        title="Distribución por Categoría"
    )
    st.plotly_chart(fig, use_container_width=True)

def show_trends_analysis(df, detected):
    """Análisis de tendencias"""
    st.header("📈 Análisis de Tendencias")
    
    if 'date' not in detected:
        st.error("No se encontró columna de fecha")
        return
    
    if 'sales' not in detected:
        st.error("No se encontró columna de ventas")
        return
    
    try:
        # Convertir fecha
        df['date_parsed'] = pd.to_datetime(df[detected['date']])
        
        # Agrupar por mes
        df['month'] = df['date_parsed'].dt.to_period('M')
        monthly_sales = df.groupby('month')[detected['sales']].sum().reset_index()
        monthly_sales['month'] = monthly_sales['month'].dt.to_timestamp()
        
        # Gráfico de línea
        fig = px.line(
            monthly_sales,
            x='month',
            y=detected['sales'],
            title="Ventas Mensuales"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al analizar tendencias: {e}")