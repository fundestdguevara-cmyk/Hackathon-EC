# ml/clustering.py
import numpy as np
import pandas as pd
from kmodes.kprototypes import KPrototypes
from sklearn.preprocessing import StandardScaler

class CustomerClustering:
    """Clustering de clientes usando K-Prototypes"""
    
    def __init__(self, n_clusters=3, init="Cao", random_state=13, verbose=0):
        self.n_clusters = n_clusters
        self.init = init
        self.random_state = random_state
        self.verbose = verbose
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_final_data(self, df, regular_clients):
        """
        Prepara los datos finales para clustering
        
        Args:
            df: DataFrame completo
            regular_clients: DataFrame de clientes regulares
            
        Returns:
            DataFrame con datos listos para clustering
        """
        # Combinar información de texto (segmento, región, etc.)
        cols_texto = ['Customer Segment', 'Order Region', 'Order City', 'Order Country']
        
        # Usar 'Order Customer Id' del df original
        info_texto = df.groupby('Order Customer Id')[cols_texto].first().reset_index()
        
        df_final = pd.merge(
            regular_clients, 
            info_texto, 
            left_on='Customer Id', 
            right_on='Order Customer Id', 
            how='left'
        )
        
        return df_final
    
    def perform_clustering(self, df_final):
        """
        Realiza clustering en los datos preparados
        
        Args:
            df_final: DataFrame preparado
            
        Returns:
            DataFrame con columna 'classification' añadida
        """
        # Separar columnas numéricas y categóricas
        cols_texto = ['Customer Segment', 'Order Region', 'Order City', 'Order Country']
        cols_num = [col for col in df_final.columns if col not in cols_texto + ['Customer Id', 'Order Customer Id']]
        
        # Asegurar que solo tenemos columnas numéricas en cols_num
        cols_num = [col for col in cols_num if col in df_final.columns and df_final[col].dtype in ['int64', 'float64']]
        
        # Escalar numéricas
        matrix_num = self.scaler.fit_transform(df_final[cols_num])
        matrix_cat = df_final[cols_texto].values
        
        # Combinar
        total_matrix = np.hstack((matrix_num, matrix_cat))
        
        # Índices de columnas categóricas
        ind_texto = list(range(matrix_num.shape[1], matrix_num.shape[1] + matrix_cat.shape[1]))
        
        # K-Prototypes
        self.model = KPrototypes(
            n_clusters=self.n_clusters,
            init=self.init,
            verbose=self.verbose,
            random_state=self.random_state
        )
        
        clusters = self.model.fit_predict(total_matrix, categorical=ind_texto)
        
        df_final["classification"] = clusters
        
        return df_final