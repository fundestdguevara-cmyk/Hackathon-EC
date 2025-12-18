from sklearn.ensemble import IsolationForest
from typing import Tuple

class AnomalyDetector:
    """Detección de anomalías en clientes"""
    
    def __init__(self, contamination: float = 0.07, random_state: int = 13):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state
        )
        self.vars_modelo = [
            "Benefit per order", "Sales per customer",
            "Order Item Discount Rate", "Order Item Quantity", "Order Id"
        ]
    
    def detect_anomalies(self, df_clients):
        """Detecta clientes anómalos"""
        df_clients["Observation_Created"] = self.model.fit_predict(
            df_clients[self.vars_modelo]
        )
        return df_clients
    
    def split_clients(self, df_clients) -> Tuple:
        """Divide en clientes regulares y raros"""
        regular_clients = df_clients[
            (df_clients["Observation_Created"] == 1) | 
            (df_clients["Benefit per order"] >= 1000)
        ]
        
        rare_clients = df_clients[
            (df_clients["Observation_Created"] == -1) & 
            (df_clients["Benefit per order"] < 1000)
        ]
        
        return regular_clients, rare_clients