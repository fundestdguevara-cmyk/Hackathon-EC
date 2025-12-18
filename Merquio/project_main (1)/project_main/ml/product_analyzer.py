# components/product_analytics.py - VERSIÓN CORREGIDA
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def render_product_analytics():
    """Renderiza el análisis de productos - Versión corregida"""
    
    st.title("📦 Análisis de Productos")
    
    # Verificar si hay datos cargados
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ Primero carga los datos en la sección 'Análisis de Clientes'")
        st.info("📝 Ve a 'Análisis de Clientes' y haz clic en 'Cargar y Procesar Datos'")
        return
    
    df = st.session_state.df
    
    # MOSTRAR INFORMACIÓN DE DEBUG
    with st.expander("🔍 Información del Dataset (Debug)"):
        st.write(f"**Filas:** {len(df):,}")
        st.write(f"**Columnas:** {len(df.columns):,}")
        st.write("**Primeras 5 columnas:**", list(df.columns)[:10])
        
        # Buscar columnas relacionadas con productos
        product_cols = []
        category_cols = []
        price_cols = []
        quantity_cols = []
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'product' in col_lower and 'name' in col_lower:
                product_cols.append(col)
            elif 'categor' in col_lower or 'type' in col_lower:
                category_cols.append(col)
            elif 'price' in col_lower or 'cost' in col_lower:
                price_cols.append(col)
            elif 'quant' in col_lower or 'qty' in col_lower:
                quantity_cols.append(col)
        
        st.write("**Posibles columnas de producto:**", product_cols)
        st.write("**Posibles columnas de categoría:**", category_cols)
        st.write("**Posibles columnas de precio:**", price_cols)
        st.write("**Posibles columnas de cantidad:**", quantity_cols)
        
        # Mostrar ejemplo de datos
        st.write("**Muestra de datos (primeras 3 filas):**")
        st.dataframe(df.head(3))
    
    # Detectar columnas automáticamente
    detected_cols = detect_product_columns(df)
    
    if not detected_cols['product_name']:
        st.error("❌ No se pudo detectar una columna de nombres de producto")
        st.info("Las columnas disponibles son:")
        st.write(list(df.columns))
        return
    
    # Menú de análisis
    st.sidebar.header("⚙️ Configuración de Análisis")
    
    analysis_type = st.sidebar.radio(
        "Tipo de análisis:",
        ["Resumen General", "Análisis por Producto", "Análisis por Categoría", "Tendencias"],
        index=0
    )
    
    # Mostrar columnas detectadas
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Columnas Detectadas")
    for key, value in detected_cols.items():
        if value:
            st.sidebar.info(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.sidebar.warning(f"**{key.replace('_', ' ').title()}:** No detectada")
    
    # Ejecutar análisis según selección
    if analysis_type == "Resumen General":
        show_general_summary(df, detected_cols)
    elif analysis_type == "Análisis por Producto":
        show_product_analysis(df, detected_cols)
    elif analysis_type == "Análisis por Categoría":
        show_category_analysis(df, detected_cols)
    elif analysis_type == "Tendencias":
        show_trends_analysis(df, detected_cols)

def detect_product_columns(df):
    """Detecta automáticamente las columnas relevantes para análisis de productos"""
    detected = {
        'product_name': None,
        'category': None,
        'price': None,
        'quantity': None,
        'sales': None,
        'discount': None,
        'benefit': None
    }
    
    # Buscar por patrones comunes
    for col in df.columns:
        col_str = str(col)
        col_lower = col_str.lower()
        
        # Nombre de producto
        if not detected['product_name']:
            if 'product' in col_lower and 'name' in col_lower:
                detected['product_name'] = col
            elif 'product' in col_lower and 'description' not in col_lower:
                detected['product_name'] = col
            elif 'item' in col_lower and 'name' in col_lower:
                detected['product_name'] = col
        
        # Categoría
        if not detected['category']:
            if 'categor' in col_lower:
                detected['category'] = col
            elif 'type' in col_lower and 'product' in col_lower:
                detected['category'] = col
            elif 'department' in col_lower:
                detected['category'] = col
            elif 'segment' in col_lower and 'product' in col_lower:
                detected['category'] = col
        
        # Precio
        if not detected['price']:
            if 'price' in col_lower:
                detected['price'] = col
            elif 'cost' in col_lower:
                detected['price'] = col
            elif 'unit' in col_lower and 'price' in col_lower:
                detected['price'] = col
        
        # Cantidad
        if not detected['quantity']:
            if 'quant' in col_lower:
                detected['quantity'] = col
            elif 'qty' in col_lower:
                detected['quantity'] = col
        
        # Ventas
        if not detected['sales']:
            if 'sales' in col_lower:
                detected['sales'] = col
            elif 'revenue' in col_lower:
                detected['sales'] = col
            elif 'total' in col_lower and 'amount' in col_lower:
                detected['sales'] = col
        
        # Descuento
        if not detected['discount']:
            if 'discount' in col_lower:
                detected['discount'] = col
            elif 'disc' in col_lower:
                detected['discount'] = col
        
        # Beneficio
        if not detected['benefit']:
            if 'benefit' in col_lower:
                detected['benefit'] = col
            elif 'profit' in col_lower:
                detected['benefit'] = col
            elif 'margin' in col_lower:
                detected['benefit'] = col
    
    return detected

def show_general_summary(df, detected_cols):
    """Muestra resumen general de productos"""
    st.header("📊 Resumen General")
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if detected_cols['product_name']:
            unique_products = df[detected_cols['product_name']].nunique()
            st.metric("Productos Únicos", f"{unique_products:,}")
        else:
            st.metric("Productos Únicos", "N/A")
    
    with col2:
        if detected_cols['sales']:
            total_sales = df[detected_cols['sales']].sum()
            st.metric("Ventas Totales", f"${total_sales:,.2f}")
        else:
            st.metric("Ventas Totales", "N/A")
    
    with col3:
        if detected_cols['quantity']:
            total_quantity = df[detected_cols['quantity']].sum()
            st.metric("Cantidad Total", f"{total_quantity:,}")
        else:
            st.metric("Cantidad Total", "N/A")
    
    with col4:
        if detected_cols['category']:
            unique_categories = df[detected_cols['category']].nunique()
            st.metric("Categorías", f"{unique_categories:,}")
        else:
            st.metric("Categorías", "N/A")
    
    st.markdown("---")
    
    # Top productos si tenemos nombre de producto
    if detected_cols['product_name'] and detected_cols['sales']:
        st.subheader("🏆 Top 10 Productos por Ventas")
        
        try:
            # Agrupar por producto
            top_products = df.groupby(detected_cols['product_name']).agg({
                detected_cols['sales']: 'sum',
                detected_cols['quantity']: 'sum' if detected_cols['quantity'] else None
            }).reset_index()
            
            # Renombrar columnas
            top_products.columns = ['Producto', 'Ventas Totales', 'Cantidad Total'] if detected_cols['quantity'] else ['Producto', 'Ventas Totales']
            
            # Ordenar y tomar top 10
            top_products = top_products.sort_values('Ventas Totales', ascending=False).head(10)
            
            # Mostrar tabla
            display_df = top_products.copy()
            display_df['Ventas Totales'] = display_df['Ventas Totales'].apply(lambda x: f"${x:,.2f}")
            if 'Cantidad Total' in display_df.columns:
                display_df['Cantidad Total'] = display_df['Cantidad Total'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Gráfico de barras
            fig = px.bar(
                top_products,
                x='Producto',
                y='Ventas Totales',
                title='Top 10 Productos por Ventas',
                color='Ventas Totales',
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al generar top productos: {str(e)}")
    
    # Distribución por categoría si tenemos categoría
    if detected_cols['category'] and detected_cols['sales']:
        st.subheader("📂 Distribución por Categoría")
        
        try:
            # Agrupar por categoría
            category_sales = df.groupby(detected_cols['category'])[detected_cols['sales']].sum().reset_index()
            category_sales.columns = ['Categoría', 'Ventas Totales']
            category_sales = category_sales.sort_values('Ventas Totales', ascending=False)
            
            # Gráfico de torta
            fig = px.pie(
                category_sales,
                values='Ventas Totales',
                names='Categoría',
                title='Distribución de Ventas por Categoría'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de categorías
            with st.expander("📊 Ver tabla de categorías"):
                display_cats = category_sales.copy()
                display_cats['Ventas Totales'] = display_cats['Ventas Totales'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(display_cats, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error al analizar categorías: {str(e)}")

def show_product_analysis(df, detected_cols):
    """Muestra análisis detallado por producto"""
    st.header("📦 Análisis por Producto")
    
    if not detected_cols['product_name']:
        st.error("No se detectó columna de nombres de producto")
        return
    
    # Configuración
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Número de productos", 5, 50, 20)
    with col2:
        sort_by = st.selectbox(
            "Ordenar por",
            ["Ventas", "Cantidad", "Frecuencia"]
        )
    
    try:
        # Agrupar por producto
        agg_dict = {}
        if detected_cols['sales']:
            agg_dict[detected_cols['sales']] = 'sum'
        if detected_cols['quantity']:
            agg_dict[detected_cols['quantity']] = 'sum'
        
        if not agg_dict:
            st.error("No hay métricas para analizar")
            return
        
        product_stats = df.groupby(detected_cols['product_name']).agg(agg_dict).reset_index()
        
        # Añadir frecuencia
        product_stats['Frecuencia'] = df.groupby(detected_cols['product_name']).size().values
        
        # Renombrar columnas
        rename_dict = {detected_cols['product_name']: 'Producto'}
        if detected_cols['sales']:
            rename_dict[detected_cols['sales']] = 'Ventas Totales'
        if detected_cols['quantity']:
            rename_dict[detected_cols['quantity']] = 'Cantidad Total'
        
        product_stats = product_stats.rename(columns=rename_dict)
        
        # Ordenar
        sort_columns = {
            "Ventas": "Ventas Totales",
            "Cantidad": "Cantidad Total",
            "Frecuencia": "Frecuencia"
        }
        
        if sort_by in sort_columns and sort_columns[sort_by] in product_stats.columns:
            product_stats = product_stats.sort_values(sort_columns[sort_by], ascending=False).head(top_n)
        
        # Mostrar resultados
        st.subheader(f"Top {top_n} Productos")
        
        # Formatear para visualización
        display_df = product_stats.copy()
        if 'Ventas Totales' in display_df.columns:
            display_df['Ventas Totales'] = display_df['Ventas Totales'].apply(lambda x: f"${x:,.2f}")
        if 'Cantidad Total' in display_df.columns:
            display_df['Cantidad Total'] = display_df['Cantidad Total'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # Gráfico
        fig = px.bar(
            product_stats,
            x='Producto',
            y=sort_columns[sort_by] if sort_by in sort_columns else 'Ventas Totales',
            title=f'Top {top_n} Productos por {sort_by}',
            color=sort_columns[sort_by] if sort_by in sort_columns else 'Ventas Totales',
            color_continuous_scale='plasma'
        )
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error en análisis por producto: {str(e)}")

def show_category_analysis(df, detected_cols):
    """Muestra análisis por categoría"""
    st.header("📂 Análisis por Categoría")
    
    if not detected_cols['category']:
        st.error("No se detectó columna de categoría")
        return
    
    try:
        # Agrupar por categoría
        agg_dict = {}
        if detected_cols['sales']:
            agg_dict[detected_cols['sales']] = 'sum'
        if detected_cols['quantity']:
            agg_dict[detected_cols['quantity']] = 'sum'
        if detected_cols['product_name']:
            agg_dict[detected_cols['product_name']] = 'nunique'
        
        if not agg_dict:
            st.error("No hay métricas para analizar")
            return
        
        category_stats = df.groupby(detected_cols['category']).agg(agg_dict).reset_index()
        
        # Renombrar columnas
        rename_dict = {detected_cols['category']: 'Categoría'}
        if detected_cols['sales']:
            rename_dict[detected_cols['sales']] = 'Ventas Totales'
        if detected_cols['quantity']:
            rename_dict[detected_cols['quantity']] = 'Cantidad Total'
        if detected_cols['product_name']:
            rename_dict[detected_cols['product_name']] = 'Productos Únicos'
        
        category_stats = category_stats.rename(columns=rename_dict)
        category_stats = category_stats.sort_values('Ventas Totales', ascending=False)
        
        # Mostrar resultados
        st.subheader("Métricas por Categoría")
        
        # Formatear para visualización
        display_df = category_stats.copy()
        if 'Ventas Totales' in display_df.columns:
            display_df['Ventas Totales'] = display_df['Ventas Totales'].apply(lambda x: f"${x:,.2f}")
        if 'Cantidad Total' in display_df.columns:
            display_df['Cantidad Total'] = display_df['Cantidad Total'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                category_stats.head(10),
                x='Categoría',
                y='Ventas Totales',
                title='Top 10 Categorías por Ventas',
                color='Ventas Totales'
            )
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            if 'Productos Únicos' in category_stats.columns:
                fig2 = px.scatter(
                    category_stats,
                    x='Productos Únicos',
                    y='Ventas Totales',
                    size='Cantidad Total' if 'Cantidad Total' in category_stats.columns else None,
                    color='Categoría',
                    title='Productos vs Ventas por Categoría',
                    hover_name='Categoría'
                )
                st.plotly_chart(fig2, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error en análisis por categoría: {str(e)}")

def show_trends_analysis(df, detected_cols):
    """Muestra análisis de tendencias"""
    st.header("📈 Análisis de Tendencias")
    
    # Verificar si hay columna de fecha
    date_cols = [col for col in df.columns if 'date' in str(col).lower()]
    
    if not date_cols:
        st.warning("No se encontraron columnas de fecha para análisis de tendencias")
        return
    
    date_column = date_cols[0]
    
    # Convertir a datetime si es necesario
    try:
        df[date_column] = pd.to_datetime(df[date_column])
    except:
        st.error(f"No se pudo convertir la columna {date_column} a fecha")
        return
    
    # Configuración
    st.sidebar.subheader("Configuración de Tendencias")
    
    time_period = st.sidebar.selectbox(
        "Periodo de tiempo",
        ["Diario", "Semanal", "Mensual", "Trimestral", "Anual"]
    )
    
    metric = st.sidebar.selectbox(
        "Métrica a analizar",
        ["Ventas", "Cantidad", "Frecuencia"]
    )
    
    # Agrupar por periodo
    df['Periodo'] = df[date_column]
    
    if time_period == "Diario":
        df['Periodo'] = df[date_column].dt.date
    elif time_period == "Semanal":
        df['Periodo'] = df[date_column].dt.to_period('W').dt.to_timestamp()
    elif time_period == "Mensual":
        df['Periodo'] = df[date_column].dt.to_period('M').dt.to_timestamp()
    elif time_period == "Trimestral":
        df['Periodo'] = df[date_column].dt.to_period('Q').dt.to_timestamp()
    elif time_period == "Anual":
        df['Periodo'] = df[date_column].dt.year
    
    try:
        # Calcular métrica
        if metric == "Ventas" and detected_cols['sales']:
            trends = df.groupby('Periodo')[detected_cols['sales']].sum().reset_index()
            trends.columns = ['Periodo', 'Valor']
            title = f'Tendencias de Ventas ({time_period})'
        elif metric == "Cantidad" and detected_cols['quantity']:
            trends = df.groupby('Periodo')[detected_cols['quantity']].sum().reset_index()
            trends.columns = ['Periodo', 'Valor']
            title = f'Tendencias de Cantidad ({time_period})'
        else:
            trends = df.groupby('Periodo').size().reset_index()
            trends.columns = ['Periodo', 'Valor']
            title = f'Tendencias de Frecuencia ({time_period})'
        
        # Ordenar por periodo
        trends = trends.sort_values('Periodo')
        
        # Gráfico de línea
        fig = px.line(
            trends,
            x='Periodo',
            y='Valor',
            title=title,
            markers=True
        )
        
        # Personalizar según métrica
        if metric == "Ventas":
            fig.update_layout(yaxis_title="Ventas ($)")
        elif metric == "Cantidad":
            fig.update_layout(yaxis_title="Cantidad")
        else:
            fig.update_layout(yaxis_title="Número de Transacciones")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla
        with st.expander("📊 Ver datos de tendencias"):
            display_trends = trends.copy()
            if metric == "Ventas":
                display_trends['Valor'] = display_trends['Valor'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_trends, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error en análisis de tendencias: {str(e)}")