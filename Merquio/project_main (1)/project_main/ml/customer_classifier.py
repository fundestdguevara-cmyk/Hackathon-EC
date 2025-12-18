import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class CustomerClassifier:
    """Clasificador de clientes en VIP, Regular u Ocasional"""
    
    def __init__(self, n_estimators=50, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.is_trained = False
        
    def train(self, df, test_size=0.2):
        """
        Entrena el clasificador
        
        Args:
            df: DataFrame con datos etiquetados
            test_size: Proporción para test
            
        Returns:
            accuracy: Precisión del modelo
        """
        features = [
            'Benefit per order', 'Sales per customer',
            'Order Item Discount Rate', 'Order Item Quantity', 'Order Id'
        ]
        
        # Eliminar filas con NaN
        mask = df[features + ['classification']].notna().all(axis=1)
        df_clean = df[mask].copy()
        
        X = df_clean[features]
        y = df_clean['classification']
        
        # Verificar que tenemos datos suficientes
        if len(X) < 10:
            raise ValueError("No hay suficientes datos limpios para entrenar")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        self.is_trained = True
        
        return accuracy
    
    def predict_customer(self, benefit, sales, discount, quantity, orders):
        """
        Clasifica un cliente nuevo
        
        Args:
            benefit: Benefit per order
            sales: Sales per customer
            discount: Order Item Discount Rate
            quantity: Order Item Quantity
            orders: Order Id (número de pedidos)
            
        Returns:
            dict: Información de clasificación
        """
        if not self.is_trained:
            raise ValueError("Modelo no entrenado. Llama a train() primero.")
        
        # Crear datos del cliente
        data = [[benefit, sales, discount, quantity, orders]]
        
        # Predecir
        category = self.model.predict(data)[0]
        probabilities = self.model.predict_proba(data)[0]
        
        # Mapear categorías
        category_map = {
            0: {"name": "CLIENTE VIP", "icon": "👑", "color": "gold"},
            1: {"name": "CLIENTE OCASIONAL", "icon": "🛍️", "color": "gray"},
            2: {"name": "CLIENTE REGULAR", "icon": "⭐", "color": "blue"}
        }
        
        info = category_map.get(category, {"name": "DESCONOCIDO", "icon": "❓", "color": "black"})
        
        return {
            "category": category,
            "name": info["name"],
            "icon": info["icon"],
            "color": info["color"],
            "probabilities": {
                "VIP": f"{probabilities[0]*100:.1f}%",
                "Ocasional": f"{probabilities[1]*100:.1f}%",
                "Regular": f"{probabilities[2]*100:.1f}%"
            }
        }