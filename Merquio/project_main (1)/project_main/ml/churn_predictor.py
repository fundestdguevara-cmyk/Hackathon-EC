import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.impute import SimpleImputer
import numpy as np

class ChurnPredictor:
    """Predicción de churn y análisis CLV"""
    
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            random_state=42
        )
        self.imputer = SimpleImputer(strategy='median')
    
    def prepare_features(self, df):
        """Prepara características para predicción de churn"""
        fecha_actual = df['order date (DateOrders)'].max()
        
        cliente_df = df.groupby('Customer Id').agg({
            'order date (DateOrders)': lambda x: (fecha_actual - x.max()).days,
            'Order Id': 'count',
            'Sales per customer': ['mean', 'sum'],
            'Benefit per order': ['mean', 'std'],
            'Late_delivery_risk': 'mean',
            'Order Item Discount Rate': 'mean',
            'Order City': 'first',
            'Order Region': 'first',
            'Category Name': lambda x: x.mode()[0] if not x.mode().empty else 'N/A'
        }).reset_index()
        
        cliente_df.columns = [
            'Customer Id', 'dias_desde_ultima_compra', 'frecuencia_compras',
            'ventas_promedio', 'Ventas_Totales', 'beneficio_promedio',
            'beneficio_std', 'late_delivery_promedio', 'descuento_promedio',
            'Ciudad', 'Region', 'Categoria_Favorita'
        ]
        
        # Reemplazar infinitos con NaN y luego manejar NaN
        cliente_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # Para std que podría ser NaN si solo hay una compra
        cliente_df['beneficio_std'].fillna(0, inplace=True)
        
        # Etiquetar riesgo
        cliente_df['riesgo_abandono'] = (
            (cliente_df['dias_desde_ultima_compra'] > 60) |
            (cliente_df['beneficio_promedio'] < 0)
        ).astype(int)
        
        return cliente_df
    
    def train_model(self, cliente_df):
        """Entrena el modelo de predicción de churn"""
        features = [
            'frecuencia_compras', 'late_delivery_promedio',
            'descuento_promedio', 'ventas_promedio', 'beneficio_std'
        ]
        
        # Eliminar filas con NaN en las features o target
        mask = cliente_df[features + ['riesgo_abandono']].notna().all(axis=1)
        cliente_df_clean = cliente_df[mask].copy()
        
        X = cliente_df_clean[features]
        y = cliente_df_clean['riesgo_abandono']
        
        # Imputar valores faltantes (por si acaso)
        X_imputed = self.imputer.fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_imputed, y, test_size=0.30, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluación
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred)
        auc = roc_auc_score(y_test, self.model.predict_proba(X_test)[:, 1])
        
        # Guardar probabilidades para todos los datos limpios
        probabilidades = self.model.predict_proba(X_imputed)[:, 1]
        cliente_df_clean['prob_abandono'] = probabilidades
        
        return cliente_df_clean, report, auc
    
    def segment_clients(self, cliente_df):
        """Segmenta clientes por valor"""
        def segmentar_valor(row):
            # Verificar que no sea NaN
            if pd.isna(row['Ventas_Totales']):
                return 'Desconocido'
            if row['Ventas_Totales'] > cliente_df['Ventas_Totales'].quantile(0.8):
                return '🥇 VIP (Alto Valor)'
            elif row['Ventas_Totales'] > cliente_df['Ventas_Totales'].quantile(0.5):
                return '🥈 Potencial'
            else:
                return '🥉 Estándar'
        
        cliente_df['Segmento_Valor'] = cliente_df.apply(segmentar_valor, axis=1)
        return cliente_df
    
    def analyze_specific_customer(self, cliente_df, customer_id):
        """Analiza un cliente específico"""
        cliente = cliente_df[cliente_df['Customer Id'] == customer_id]
        
        if cliente.empty:
            return None
        
        row = cliente.iloc[0]
        
        # Preparar features para predicción
        features = ['frecuencia_compras', 'late_delivery_promedio',
                   'descuento_promedio', 'ventas_promedio', 'beneficio_std']
        
        X_customer = row[features].values.reshape(1, -1)
        X_imputed = self.imputer.transform(X_customer)
        
        prob = self.model.predict_proba(X_imputed)[0, 1]
        
        return {
            'customer_id': customer_id,
            'prob_abandono': prob,
            'segmento': row.get('Segmento_Valor', 'Desconocido'),
            'ventas_totales': row.get('Ventas_Totales', 0),
            'dias_inactivo': row.get('dias_desde_ultima_compra', 0),
            'ciudad': row.get('Ciudad', 'Desconocido'),
            'region': row.get('Region', 'Desconocido'),
            'categoria_favorita': row.get('Categoria_Favorita', 'Desconocido')
        }