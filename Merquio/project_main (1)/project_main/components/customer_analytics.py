import streamlit as st
import pandas as pd
import time
from data.data_loader import SupplyChainDataLoader
from ml.anomaly_detection import AnomalyDetector
from ml.clustering import CustomerClustering
from ml.customer_classifier import CustomerClassifier

def render_customer_analytics():
    """Renderiza el análisis completo de clientes"""
    
    st.title("🔍 Análisis Avanzado de Clientes")
    
    # Opción para usar datos pre-computados
    use_precomputed = st.checkbox("Usar clusters pre-computados (recomendado)", value=True)
    
    # Paso 1: Cargar datos
    if st.button("📥 Cargar y Procesar Datos"):
        with st.spinner("Procesando datos..."):
            start_time = time.time()
            
            loader = SupplyChainDataLoader()
            
            if use_precomputed:
                # Intentar cargar clusters pre-computados
                precomputed = loader.load_precomputed_clusters()
                
                if precomputed:
                    # Usar datos pre-computados
                    st.session_state.df = precomputed['df']
                    st.session_state.df_clients = precomputed['df_clients']
                    st.session_state.regular_clients = precomputed['regular_clients']
                    st.session_state.rare_clients = precomputed['rare_clients']
                    st.session_state.df_final = precomputed['df_final']
                    st.session_state.data_loaded = True
                    
                    elapsed = time.time() - start_time
                    st.success(f"✅ Datos cargados en {elapsed:.2f} segundos (pre-computados)")
                else:
                    # Calcular en tiempo real
                    st.info("⚠️ No hay clusters pre-computados. Calculando ahora...")
                    df = loader.load_data()
                    df_clients = loader.prepare_client_data(df)
                    
                    detector = AnomalyDetector()
                    df_clients = detector.detect_anomalies(df_clients)
                    regular_clients, rare_clients = detector.split_clients(df_clients)
                    
                    st.warning("⚠️ K-Prototypes puede tardar varios minutos...")
                    clustering = CustomerClustering(verbose=0)
                    df_final = clustering.prepare_final_data(df, regular_clients)
                    df_final = clustering.perform_clustering(df_final)
                    
                    # Guardar en sesión
                    st.session_state.df = df
                    st.session_state.df_clients = df_clients
                    st.session_state.regular_clients = regular_clients
                    st.session_state.rare_clients = rare_clients
                    st.session_state.df_final = df_final
                    st.session_state.data_loaded = True
                    
                    # Guardar pre-computado para futuras ejecuciones
                    results = {
                        'df': df,
                        'df_clients': df_clients,
                        'regular_clients': regular_clients,
                        'rare_clients': rare_clients,
                        'df_final': df_final
                    }
                    loader.save_precomputed_clusters(results)
                    
                    elapsed = time.time() - start_time
                    st.success(f"✅ Datos procesados en {elapsed:.2f} segundos")
            else:
                # Calcular siempre en tiempo real
                df = loader.load_data()
                df_clients = loader.prepare_client_data(df)
                
                detector = AnomalyDetector()
                df_clients = detector.detect_anomalies(df_clients)
                regular_clients, rare_clients = detector.split_clients(df_clients)
                
                st.warning("⚠️ K-Prototypes puede tardar varios minutos...")
                clustering = CustomerClustering(verbose=0)
                df_final = clustering.prepare_final_data(df, regular_clients)
                df_final = clustering.perform_clustering(df_final)
                
                st.session_state.df = df
                st.session_state.df_clients = df_clients
                st.session_state.regular_clients = regular_clients
                st.session_state.rare_clients = rare_clients
                st.session_state.df_final = df_final
                st.session_state.data_loaded = True
                
                elapsed = time.time() - start_time
                st.success(f"✅ Datos procesados en {elapsed:.2f} segundos")
    
    # Mostrar datos si están cargados
    if st.session_state.get('data_loaded', False):
        display_customer_analysis()

def display_customer_analysis():
    """Muestra el análisis de clientes ya cargado"""
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Clientes Totales", len(st.session_state.df_clients))
    with col2:
        st.metric("Clientes Regulares", len(st.session_state.regular_clients))
    with col3:
        st.metric("Clientes Anómalos", len(st.session_state.rare_clients))
    with col4:
        if 'df_final' in st.session_state:
            clusters = st.session_state.df_final['classification'].nunique()
            st.metric("Clusters", clusters)
    
    # Mostrar resultados del clustering
    if 'df_final' in st.session_state:
        st.subheader("📊 Resultados del Clustering (K-Prototypes)")
        
        # Mostrar distribución de clusters
        cluster_dist = st.session_state.df_final['classification'].value_counts().sort_index()
        
        cols = st.columns(3)
        cluster_names = {0: "👑 VIP", 1: "🛍️ Ocasional", 2: "⭐ Regular"}
        
        for i, (cluster, count) in enumerate(cluster_dist.items()):
            with cols[i % 3]:
                name = cluster_names.get(cluster, f"Cluster {cluster}")
                st.metric(f"{name}", f"{count:,}")
        
        # Mostrar tabla resumen
        resumen = st.session_state.df_final.groupby('classification').agg({
            'Benefit per order': 'mean',
            'Sales per customer': 'mean',
            'Order Item Quantity': 'mean',
            'Order Id': 'mean'
        }).round(2)
        
        resumen.columns = ['Beneficio Promedio', 'Ventas Promedio', 'Cantidad Promedio', 'Pedidos Promedio']
        
        st.subheader("📈 Características por Cluster")
        st.dataframe(resumen)
        
        # Mostrar algunos ejemplos
        with st.expander("👀 Ver ejemplos de clientes por cluster"):
            for cluster in sorted(st.session_state.df_final['classification'].unique()):
                st.markdown(f"**{cluster_names.get(cluster, f'Cluster {cluster}')}**")
                sample = st.session_state.df_final[
                    st.session_state.df_final['classification'] == cluster
                ].head(3)
                
                for _, row in sample.iterrows():
                    st.write(f"- ID {row['Customer Id']}: ${row['Benefit per order']:.2f} beneficio, ${row['Sales per customer']:.2f} ventas")
    
    # Clasificación de nuevo cliente (igual que antes)
    st.subheader("🎯 Clasificar Nuevo Cliente")
    
    with st.form("cliente_form"):
        col1, col2 = st.columns(2)
        with col1:
            beneficio = st.number_input("Beneficio por orden", value=1500.0, min_value=0.0)
            ventas = st.number_input("Ventas por cliente", value=5000.0, min_value=0.0)
        with col2:
            descuento = st.slider("Tasa de descuento", 0.0, 1.0, 0.08, 0.01)
            cantidad = st.number_input("Cantidad promedio", value=2.8, min_value=0.1)
            pedidos = st.number_input("Número de pedidos", value=10, min_value=1)
        
        submitted = st.form_submit_button("Clasificar Cliente")
        
        if submitted and 'df_final' in st.session_state:
            try:
                classifier = CustomerClassifier()
                
                # Entrenar modelo con datos pre-computados
                df_final = st.session_state.df_final
                X = df_final[['Benefit per order', 'Sales per customer',
                            'Order Item Discount Rate', 'Order Item Quantity', 'Order Id']]
                y = df_final['classification']
                
                # ELIMINAR NaN antes de entrenar
                mask = X.notna().all(axis=1) & y.notna()
                X = X[mask]
                y = y[mask]
                
                # Entrenar modelo
                accuracy = classifier.train(df_final[mask])  # <-- LLAMAR A train()
                
                # Clasificar nuevo cliente
                resultado = classifier.predict_customer(
                    beneficio, ventas, descuento, cantidad, pedidos
                )
                
                # Mostrar resultado
                st.success(f"{resultado['icon']} **{resultado['name']}**")
                
                # Mostrar probabilidades en barras
                probs = {
                    'VIP': float(resultado['probabilities']['VIP'].replace('%', '')) / 100,
                    'Ocasional': float(resultado['probabilities']['Ocasional'].replace('%', '')) / 100,
                    'Regular': float(resultado['probabilities']['Regular'].replace('%', '')) / 100
                }
                
                # Gráfico de probabilidades
                import plotly.graph_objects as go
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(probs.keys()),
                        y=list(probs.values()),
                        text=[f"{v*100:.1f}%" for v in probs.values()],
                        textposition='auto',
                        marker_color=['gold', 'gray', 'blue']
                    )
                ])
                fig.update_layout(
                    title="Probabilidades de Clasificación",
                    yaxis=dict(range=[0, 1], tickformat=".0%"),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error al clasificar cliente: {str(e)}")