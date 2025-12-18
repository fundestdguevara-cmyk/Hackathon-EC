import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import gdown
import os
from typing import Tuple
import pickle
from typing import Tuple, Dict

file_path = "https://raw.githubusercontent.com/Sr-Bady/HACKEATHON_SAMSUNG_G3/refs/heads/main/SuperMarket%20Analysis.csv" #repositorio en github
products_path = "/root/.cache/kagglehub/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints/versions/1/BigBasket Products.csv"
@st.cache_data
def load_sample_data():
    """Cargar datos de ejemplo similares a los del proyecto"""
    np.random.seed(42)
    
    # Crear fechas como objetos datetime de Python
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 3, 31)
    
    # Crear 1000 fechas aleatorias
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    random_dates = np.random.choice(date_range, 1000)
    
    # Convertir a objetos datetime de Python
    python_dates = [pd.Timestamp(date) for date in random_dates]
    
    # Crear datos
    data = {
        'Invoice ID': [f'INV-{i:05d}' for i in range(1000)],
        'Branch': np.random.choice(['A', 'B', 'C'], 1000),
        'City': np.random.choice(['Mandalay', 'Naypyitaw', 'Yangon'], 1000),
        'Customer type': np.random.choice(['Member', 'Normal'], 1000),
        'Gender': np.random.choice(['Male', 'Female'], 1000),
        'Product line': np.random.choice([
            'Electronic accessories',
            'Fashion accessories',
            'Food and beverages',
            'Health and beauty',
            'Home and lifestyle',
            'Sports and travel'
        ], 1000),
        'Date': python_dates,
        'Time': [d.time() for d in python_dates],
        'Payment': np.random.choice(['Cash', 'Credit card', 'Ewallet'], 1000),
        'Quantity': np.random.randint(1, 10, 1000),
        'Sales': np.random.uniform(10, 1000, 1000).round(2)
    }
    
    df = pd.DataFrame(data)
    df['weekday'] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    return df

def load_real_data(file_path):
    """Cargar datos reales desde un archivo CSV"""
    try:
        df = pd.read_csv(file_path)
        # Convertir columnas de fecha si existen
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df['Month'] = df['Date'].dt.month
            df['Year'] = df['Date'].dt.year
            df['weekday'] = df['Date'].dt.day_name()
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None

class SupplyChainDataLoader:
    """Cargador del dataset de cadena de suministro"""
    
    def __init__(self, file_id: str = '1VNArYveijKBtBKdIo7YCbVQITWxuyTQc'):
        self.file_id = file_id
        self.data_path = "DataCoSupplyChainDataset.csv"
        self.precomputed_path = "precomputed_data/clusters.pkl"
        
    def download_data(self) -> None:
        """Descarga el dataset desde Google Drive"""
        if not os.path.exists(self.data_path):
            url = f'https://drive.google.com/uc?id={self.file_id}'
            gdown.download(url, self.data_path, quiet=False)
    
    def load_data(self, use_precomputed: bool = True) -> pd.DataFrame:
        """Carga y limpia los datos iniciales"""
        self.download_data()
        
        df = pd.read_csv(self.data_path, encoding='latin-1')
        
        # Limpieza básica
        df.dropna(subset=['Customer Lname', 'Customer Zipcode'], inplace=True)
        df = df.drop(columns=[
            'Customer Email', 'Customer Password',
            'Product Image', 'Product Description',
            'Order Zipcode'
        ])
        
        # Conversión de fechas
        df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'])
        
        return df
    
    def prepare_client_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara datos agregados por cliente"""
        df_clients = df.groupby("Customer Id").agg({
            'Benefit per order': "sum",
            'Sales per customer': "sum",
            'Order Item Discount Rate': 'mean',
            'Order Item Quantity': 'mean',
            'Order Id': 'nunique'
        }).reset_index()
        
        return df_clients
    
    def load_precomputed_clusters(self) -> Dict:
        """Carga clusters pre-computados si existen"""
        if os.path.exists(self.precomputed_path):
            with open(self.precomputed_path, 'rb') as f:
                return pickle.load(f)
        return None
    
    def save_precomputed_clusters(self, data_dict: Dict) -> None:
        """Guarda clusters pre-computados"""
        os.makedirs('precomputed_data', exist_ok=True)
        with open(self.precomputed_path, 'wb') as f:
            pickle.dump(data_dict, f)