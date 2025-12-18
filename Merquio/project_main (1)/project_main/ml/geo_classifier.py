import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class GeoClassifier:
    """Clasificador geográfico para diferentes niveles"""
    
    def __init__(self, level="region", n_estimators=250, random_state=42):
        """
        Inicializa clasificador geográfico
        
        Args:
            level: Nivel de clasificación ('region', 'country', 'state', 'city')
            n_estimators: Número de árboles en RandomForest
        """
        self.level = level
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_encoders = {}
        self.is_trained = False
        
    def prepare_features(self, df, feature_columns):
        """
        Prepara características para el modelo
        
        Args:
            df: DataFrame con datos
            feature_columns: Columnas a usar como features
            
        Returns:
            X: Características preparadas
        """
        X = df[feature_columns].copy()
        
        # Codificar variables categóricas
        for col in X.select_dtypes(include="object").columns:
            if col not in self.feature_encoders:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.feature_encoders[col] = le
            else:
                le = self.feature_encoders[col]
                X[col] = le.transform(X[col].astype(str))
        
        return X
    
    def train(self, df, feature_columns, target_column, test_size=0.25):
        """
        Entrena el clasificador
        
        Args:
            df: DataFrame con datos
            feature_columns: Columnas de características
            target_column: Columna objetivo
            test_size: Proporción para test
            
        Returns:
            dict: Métricas de rendimiento
        """
        # Preparar características
        X = self.prepare_features(df, feature_columns)
        
        # Preparar objetivo
        y = df[target_column]
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Escalar características
        X_scaled = self.scaler.fit_transform(X)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, 
            test_size=test_size, 
            random_state=42, 
            stratify=y_encoded
        )
        
        # Entrenar modelo
        self.model.fit(X_train, y_train)
        
        # Evaluar
        y_pred = self.model.predict(X_test)
        
        self.is_trained = True
        
        return {
            "accuracy": accuracy_score(y_test, y_pred),
            "report": classification_report(
                self.label_encoder.inverse_transform(y_test),
                self.label_encoder.inverse_transform(y_pred)
            )
        }
    
    def predict(self, features_dict):
        """
        Predice la ubicación geográfica
        
        Args:
            features_dict: Diccionario con características
            
        Returns:
            str: Predicción de ubicación
        """
        if not self.is_trained:
            raise ValueError("Modelo no entrenado. Llama a train() primero.")
        
        # Convertir a DataFrame
        features_df = pd.DataFrame([features_dict])
        
        # Preparar características (codificar y escalar)
        for col in features_df.columns:
            if col in self.feature_encoders:
                le = self.feature_encoders[col]
                features_df[col] = le.transform(features_df[col].astype(str))
        
        features_scaled = self.scaler.transform(features_df)
        
        # Predecir
        prediction_encoded = self.model.predict(features_scaled)[0]
        prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        return prediction