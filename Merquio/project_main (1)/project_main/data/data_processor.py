import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(filepath):
    """
    Carga y preprocesa los datos del supply chain
    
    Args:
        filepath: Ruta al archivo CSV
        
    Returns:
        dict: Diccionario con DataFrames procesados
    """
    # Cargar datos
    df = pd.read_csv(filepath, encoding='latin-1')
    
    # Limpieza inicial
    df = df.dropna(subset=['Customer Lname', 'Customer Zipcode'])
    
    # Eliminar columnas no necesarias
    columns_to_drop = [
        'Customer Email', 'Customer Password',
        'Product Image', 'Product Description', 'Order Zipcode'
    ]
    df = df.drop(columns=columns_to_drop)
    
    # Agregar datos por cliente
    df_clients = df.groupby("Customer Id").agg({
        'Benefit per order': "sum",
        'Sales per customer': "sum",
        'Order Item Discount Rate': 'mean',
        'Order Item Quantity': 'mean',
        'Order Id': 'nunique'
    }).reset_index()
    
    # Clasificar columnas por tipo
    text_cols = []
    numeric_cols = []
    
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
            text_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
    
    return {
        'full_data': df,
        'clients_data': df_clients,
        'text_columns': text_cols,
        'numeric_columns': numeric_cols
    }

def add_customer_segments(df_clients, df_full, segment_columns):
    """
    Añade segmentos de cliente al DataFrame agregado
    
    Args:
        df_clients: DataFrame agregado por cliente
        df_full: DataFrame completo
        segment_columns: Columnas para segmentación
        
    Returns:
        DataFrame: DataFrame enriquecido con segmentos
    """
    # Obtener información de segmento del cliente
    segment_info = df_full.groupby('Customer Id')[segment_columns].first().reset_index()
    
    # Fusionar con datos de clientes
    df_enriched = pd.merge(
        df_clients, 
        segment_info, 
        left_on='Customer Id', 
        right_on='Customer Id', 
        how='left'
    )
    
    return df_enriched