import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.data_loader import SupplyChainDataLoader
from ml.churn_predictor import ChurnPredictor

def render_churn_analytics():
    """Renderiza el análisis de churn y CLV"""
    
    st.title("📈 Predicción de Churn y Valor de Vida del Cliente")
    
    # Paso 1: Cargar datos
    if st.button("📥 Cargar y Analizar Datos de Churn"):
        with st.spinner("Analizando datos de churn..."):
            loader = SupplyChainDataLoader()
            df = loader.load_data()
            
            # Preparar datos para churn
            predictor = ChurnPredictor()
            cliente_df = predictor.prepare_features(df)
            
            # Entrenar modelo
            try:
                cliente_df, report, auc = predictor.train_model(cliente_df)
                cliente_df = predictor.segment_clients(cliente_df)
                
                # Guardar en estado de sesión
                st.session_state.cliente_df = cliente_df
                st.session_state.churn_report = report
                st.session_state.churn_auc = auc
                st.session_state.churn_predictor = predictor
                
                st.success("✅ Análisis de churn completado!")
                
                # Mostrar estadísticas
                st.info(f"""
                **Estadísticas del modelo:**
                - Clientes analizados: {len(cliente_df):,}
                - AUC Score: {auc:.4f}
                - Clientes en riesgo: {(cliente_df['riesgo_abandono'] == 1).sum():,}
                - Clientes VIP: {(cliente_df['Segmento_Valor'] == '🥇 VIP (Alto Valor)').sum():,}
                """)
                
            except Exception as e:
                st.error(f"Error al entrenar modelo: {str(e)}")
                st.info("Verificando datos...")
                st.write("Primeras filas del dataset:", cliente_df.head())
                st.write("Valores NaN por columna:", cliente_df.isna().sum())
                return
    
    if 'cliente_df' in st.session_state:
        cliente_df = st.session_state.cliente_df
        predictor = st.session_state.churn_predictor
        
        # Mostrar métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clientes", f"{len(cliente_df):,}")
        with col2:
            riesgo = (cliente_df['riesgo_abandono'] == 1).sum()
            st.metric("Clientes en Riesgo", f"{riesgo:,}")
        with col3:
            st.metric("AUC Score", f"{st.session_state.churn_auc:.4f}")
        with col4:
            vip_count = (cliente_df['Segmento_Valor'] == '🥇 VIP (Alto Valor)').sum()
            st.metric("Clientes VIP", f"{vip_count:,}")
        
        # Distribución de segmentos
        st.subheader("📊 Distribución de Segmentos")
        segment_counts = cliente_df['Segmento_Valor'].value_counts()
        
        fig1 = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title='Distribución de Clientes por Segmento'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Clientes con mayor riesgo
        st.subheader("📋 Clientes con Mayor Riesgo de Abandono")
        
        col1, col2 = st.columns(2)
        with col1:
            top_n = st.slider("Número de clientes a mostrar", 5, 50, 10)
        
        with col2:
            segment_filter = st.selectbox(
                "Filtrar por segmento",
                ["Todos"] + list(cliente_df['Segmento_Valor'].unique())
            )
        
        top_risk = cliente_df.copy()
        if segment_filter != "Todos":
            top_risk = top_risk[top_risk['Segmento_Valor'] == segment_filter]
        
        top_risk = top_risk.sort_values('prob_abandono', ascending=False).head(top_n)
        
        # Formatear para mostrar
        display_df = top_risk[['Customer Id', 'prob_abandono', 'Segmento_Valor', 
                              'Ventas_Totales', 'dias_desde_ultima_compra']].copy()
        display_df['prob_abandono'] = display_df['prob_abandono'].apply(lambda x: f"{x*100:.1f}%")
        display_df['Ventas_Totales'] = display_df['Ventas_Totales'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # Buscar cliente específico
        st.subheader("🔍 Analizar Cliente Específico")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            customer_id = st.number_input("ID del Cliente", min_value=1, step=1, 
                                         value=int(cliente_df['Customer Id'].iloc[0]))
        
        with col2:
            st.write("")  # Espacio
            if st.button("Analizar Cliente", type="primary"):
                cliente_info = predictor.analyze_specific_customer(cliente_df, customer_id)
                
                if cliente_info:
                    # Mostrar información
                    st.markdown(f"### 📋 Información del Cliente: {customer_id}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Segmento", cliente_info['segmento'])
                    with col2:
                        st.metric("Prob. Abandono", f"{cliente_info['prob_abandono']*100:.1f}%")
                    with col3:
                        st.metric("Ventas Totales", f"${cliente_info['ventas_totales']:,.2f}")
                    
                    # Información adicional
                    col4, col5 = st.columns(2)
                    with col4:
                        st.metric("Días Inactivo", f"{cliente_info['dias_inactivo']}")
                    with col5:
                        st.metric("Región", cliente_info['region'])
                    
                    # Recomendaciones
                    st.subheader("🎯 Recomendaciones")
                    
                    if cliente_info['prob_abandono'] > 0.7:
                        st.error("⚠️ **ALTO RIESGO**: Cliente en riesgo crítico de abandono")
                        st.markdown("""
                        **Acciones recomendadas:**
                        1. 📞 **Contacto directo** del equipo de retención
                        2. 🎁 **Oferta especial** de rescate (30% descuento en próxima compra)
                        3. 📝 **Encuesta de satisfacción** prioritaria
                        4. 🚚 **Envío gratis** en próxima compra
                        """)
                    elif cliente_info['prob_abandono'] > 0.4:
                        st.warning("⚠️ **RIESGO MODERADO**: Monitorear de cerca")
                        st.markdown("""
                        **Acciones recomendadas:**
                        1. 📧 **Email personalizado** con oferta (15% descuento)
                        2. 💎 **Programa de fidelización** personalizado
                        3. 🔔 **Recordatorios** de productos relacionados
                        4. ⭐ **Programa de referidos** con beneficios
                        """)
                    else:
                        st.success("✅ **BAJO RIESGO**: Cliente saludable")
                        st.markdown("""
                        **Acciones recomendadas:**
                        1. 📨 **Mantener comunicación** regular (newsletter mensual)
                        2. ⬆️ **Ofrecer upgrades** o productos premium
                        3. 🤝 **Programa de lealtad** con beneficios exclusivos
                        4. 📊 **Cross-selling** con productos relacionados
                        """)
                    
                    # Sugerencia específica por categoría favorita
                    if cliente_info['categoria_favorita'] != 'Desconocido':
                        st.info(f"💡 **Sugerencia**: Ofrecer productos nuevos de la categoría **{cliente_info['categoria_favorita']}**")
                else:
                    st.error(f"❌ Cliente {customer_id} no encontrado")