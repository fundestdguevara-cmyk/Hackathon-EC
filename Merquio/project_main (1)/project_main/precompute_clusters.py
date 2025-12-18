import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import gdown
import os
import pickle
from typing import Tuple, Dict

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