"""
Módulo de análisis comparativo para lenguajes de señas.

Este módulo proporciona funcionalidades para analizar correlaciones,
similitudes y patrones entre diferentes lenguajes de señas.

Autor: Signify Team
Versión: 1.0.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from database.signs_database import SignsDatabase, SignEntry


class ComparativeAnalyzer:
    """
    Analizador comparativo para lenguajes de señas.
    
    Proporciona métodos para análisis estadístico y visualización
    de similitudes entre diferentes lenguajes de señas.
    """
    
    def __init__(self, database: SignsDatabase):
        """
        Inicializa el analizador comparativo.
        
        Args:
            database: Base de datos de señas multiidioma
        """
        self.database = database
        self.common_words = self.database.get_common_words()
        self.languages = list(self.database.signs.keys())
        
        # Configurar estilo de matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def get_common_words_data(self) -> pd.DataFrame:
        """
        Obtiene un DataFrame con las palabras comunes y sus descripciones.
        
        Returns:
            DataFrame con columnas: palabra, idioma, descripcion, longitud
        """
        data = []
        
        for word in self.common_words:
            for language in self.languages:
                sign_entry = self.database.search_exact(word, language)
                if sign_entry:
                    data.append({
                        'palabra': word,
                        'idioma': language,
                        'descripcion': sign_entry.instructions,
                        'longitud': len(sign_entry.instructions),
                        'categoria': sign_entry.category
                    })
        
        return pd.DataFrame(data)
    
    def calculate_text_similarity_matrix(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Calcula matriz de similitud basada en las descripciones de texto.
        
        Returns:
            Tupla con DataFrame de datos y matriz de similitud
        """
        df = self.get_common_words_data()
        
        # Crear matriz de características TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Mantener todas las palabras para español
            ngram_range=(1, 2)
        )
        
        # Agrupar descripciones por idioma
        language_texts = {}
        for language in self.languages:
            texts = df[df['idioma'] == language]['descripcion'].tolist()
            language_texts[language] = ' '.join(texts)
        
        # Vectorizar textos
        texts_list = [language_texts[lang] for lang in self.languages]
        tfidf_matrix = vectorizer.fit_transform(texts_list)
        
        # Calcular similitud coseno
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        return df, similarity_matrix
    
    def calculate_spearman_correlation(self) -> pd.DataFrame:
        """
        Calcula correlación de Spearman entre idiomas basada en longitudes de descripción.
        
        Returns:
            Matriz de correlación de Spearman
        """
        df = self.get_common_words_data()
        
        # Crear matriz pivote con longitudes
        pivot_df = df.pivot(index='palabra', columns='idioma', values='longitud')
        
        # Calcular correlación de Spearman
        correlation_matrix = pivot_df.corr(method='spearman')
        
        return correlation_matrix
    
    def perform_statistical_tests(self) -> Dict[str, Any]:
        """
        Realiza pruebas estadísticas de significancia entre idiomas.
        
        Returns:
            Diccionario con resultados de pruebas estadísticas
        """
        df = self.get_common_words_data()
        results = {}
        
        # Prueba de Kruskal-Wallis para diferencias entre grupos
        groups = [df[df['idioma'] == lang]['longitud'].values for lang in self.languages]
        kruskal_stat, kruskal_p = stats.kruskal(*groups)
        
        results['kruskal_wallis'] = {
            'statistic': kruskal_stat,
            'p_value': kruskal_p,
            'significant': kruskal_p < 0.05
        }
        
        # Pruebas de Mann-Whitney U entre pares de idiomas
        mann_whitney_results = {}
        for i, lang1 in enumerate(self.languages):
            for j, lang2 in enumerate(self.languages[i+1:], i+1):
                group1 = df[df['idioma'] == lang1]['longitud'].values
                group2 = df[df['idioma'] == lang2]['longitud'].values
                
                stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
                
                mann_whitney_results[f'{lang1}_vs_{lang2}'] = {
                    'statistic': stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
        
        results['mann_whitney'] = mann_whitney_results
        
        # Prueba de Friedman para medidas repetidas
        pivot_df = df.pivot(index='palabra', columns='idioma', values='longitud')
        if not pivot_df.isnull().any().any():
            friedman_stat, friedman_p = stats.friedmanchisquare(*[pivot_df[lang].values for lang in self.languages])
            results['friedman'] = {
                'statistic': friedman_stat,
                'p_value': friedman_p,
                'significant': friedman_p < 0.05
            }
        
        return results
    
    def calculate_association_coefficients(self) -> Dict[str, pd.DataFrame]:
        """
        Calcula diferentes coeficientes de asociación entre idiomas.
        
        Returns:
            Diccionario con matrices de coeficientes
        """
        df = self.get_common_words_data()
        pivot_df = df.pivot(index='palabra', columns='idioma', values='longitud')
        
        coefficients = {}
        
        # Coeficiente de correlación de Pearson
        coefficients['pearson'] = pivot_df.corr(method='pearson')
        
        # Coeficiente de correlación de Spearman
        coefficients['spearman'] = pivot_df.corr(method='spearman')
        
        # Coeficiente de correlación de Kendall
        coefficients['kendall'] = pivot_df.corr(method='kendall')
        
        return coefficients
    
    def perform_correspondence_analysis(self) -> Dict[str, Any]:
        """
        Realiza análisis de correspondencia para visualizar patrones.
        
        Returns:
            Diccionario con resultados del análisis de correspondencia
        """
        df = self.get_common_words_data()
        
        if df.empty:
            return {
                'contingency_table': pd.DataFrame(),
                'row_coordinates': pd.DataFrame(),
                'col_coordinates': pd.DataFrame(),
                'explained_variance': pd.Series(),
                'error': 'No hay datos suficientes para el análisis'
            }
        
        # Crear tabla de contingencia (palabra x idioma con longitudes)
        contingency_table = df.pivot_table(
            index='palabra', 
            columns='idioma', 
            values='longitud', 
            fill_value=0
        )
        
        # Verificar que tenemos suficientes datos
        if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
            return {
                'contingency_table': contingency_table,
                'row_coordinates': pd.DataFrame(),
                'col_coordinates': pd.DataFrame(),
                'explained_variance': pd.Series(),
                'error': 'Datos insuficientes para análisis de correspondencia'
            }
        
        try:
            # Realizar análisis de correspondencia simplificado usando PCA
            # Determinar el número de componentes basado en las dimensiones reales
            max_components = min(contingency_table.shape[0], contingency_table.shape[1]) - 1
            n_components = min(2, max_components)
            if n_components < 1:
                n_components = 1
            
            # Análisis para idiomas (columnas de la tabla de contingencia)
            scaler_idiomas = StandardScaler()
            scaled_idiomas = scaler_idiomas.fit_transform(contingency_table.T)
            
            pca_idiomas = PCA(n_components=n_components)
            idiomas_coordinates = pca_idiomas.fit_transform(scaled_idiomas)
            
            # Crear DataFrame para coordenadas de idiomas
            row_coords = pd.DataFrame(
                idiomas_coordinates,
                index=contingency_table.columns,
                columns=[f'Dim{i+1}' for i in range(n_components)]
            )
            
            # Análisis para palabras (filas de la tabla de contingencia)
            if contingency_table.shape[0] > 1:
                scaler_palabras = StandardScaler()
                scaled_palabras = scaler_palabras.fit_transform(contingency_table)
                
                # Usar el mismo número de componentes para consistencia
                pca_palabras = PCA(n_components=n_components)
                palabras_coordinates = pca_palabras.fit_transform(scaled_palabras)
                
                col_coords = pd.DataFrame(
                    palabras_coordinates,
                    index=contingency_table.index,
                    columns=[f'Dim{i+1}' for i in range(n_components)]
                )
            else:
                col_coords = pd.DataFrame()
            
            explained_variance = pd.Series(
                pca_idiomas.explained_variance_ratio_,
                index=[f'Dim{i+1}' for i in range(n_components)]
            )
            
            return {
                'contingency_table': contingency_table,
                'row_coordinates': row_coords,
                'col_coordinates': col_coords,
                'explained_variance': explained_variance,
                'error': None
            }
            
        except Exception as e:
            return {
                'contingency_table': contingency_table,
                'row_coordinates': pd.DataFrame(),
                'col_coordinates': pd.DataFrame(),
                'explained_variance': pd.Series(),
                'error': f'Error en análisis de correspondencia: {str(e)}'
            }
    
    def create_correlation_heatmap(self, method: str = 'spearman') -> go.Figure:
        """
        Crea un mapa de calor de correlaciones.
        
        Args:
            method: Método de correlación ('spearman', 'kendall', 'pearson')
            
        Returns:
            Figura de Plotly con el mapa de calor
        """
        if method == 'spearman':
            corr_matrix = self.calculate_spearman_correlation()
        elif method == 'kendall':
            corr_matrix = self.calculate_kendall_tau()
        else:
            coefficients = self.calculate_association_coefficients()
            corr_matrix = coefficients['pearson']
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 3),
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=dict(
                text=f'Matriz de Correlación {method.title()} entre Idiomas de Señas',
                font=dict(size=18, color='#FFFFFF', family='Arial'),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text='Idiomas', font=dict(size=16, color='#FFFFFF', family='Arial')),
                tickfont=dict(size=14, color='#FFFFFF', family='Arial'),
                linecolor='#FFFFFF',
                linewidth=3,
                gridcolor='#444444',
                gridwidth=2,
                showgrid=True
            ),
            yaxis=dict(
                title=dict(text='Idiomas', font=dict(size=16, color='#FFFFFF', family='Arial')),
                tickfont=dict(size=14, color='#FFFFFF', family='Arial'),
                linecolor='#FFFFFF',
                linewidth=3,
                gridcolor='#444444',
                gridwidth=2,
                showgrid=True
            ),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            width=600,
            height=500,
            font=dict(color='#FFFFFF', family='Arial')
        )
        
        # Forzar configuración de contraste adicional
        fig.update_traces(
            textfont=dict(color='#FFFFFF', size=12, family='Arial')
        )
        
        return fig
    
    def create_similarity_heatmap(self) -> go.Figure:
        """
        Crea un mapa de calor de similitudes de texto.
        
        Returns:
            Figura de Plotly con el mapa de calor
        """
        df, similarity_matrix = self.calculate_text_similarity_matrix()
        
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=self.languages,
            y=self.languages,
            colorscale='Viridis',
            text=np.round(similarity_matrix, 3),
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=dict(
                text='Matriz de Similitud de Texto entre Idiomas de Señas',
                font=dict(size=18, color='#FFFFFF', family='Arial'),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text='Idiomas', font=dict(size=16, color='#FFFFFF', family='Arial')),
                tickfont=dict(size=14, color='#FFFFFF', family='Arial'),
                linecolor='#FFFFFF',
                linewidth=3,
                gridcolor='#444444',
                gridwidth=2,
                showgrid=True
            ),
            yaxis=dict(
                title=dict(text='Idiomas', font=dict(size=16, color='#FFFFFF', family='Arial')),
                tickfont=dict(size=14, color='#FFFFFF', family='Arial'),
                linecolor='#FFFFFF',
                linewidth=3,
                gridcolor='#444444',
                gridwidth=2,
                showgrid=True
            ),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            width=600,
            height=500,
            font=dict(color='#FFFFFF', family='Arial')
        )
        
        # Forzar configuración de contraste adicional
        fig.update_traces(
            textfont=dict(color='#FFFFFF', size=12, family='Arial')
        )
        
        return fig
    
    def create_correspondence_plot(self) -> go.Figure:
        """
        Crea un gráfico de análisis de correspondencia.
        
        Returns:
            Figura de Plotly con el análisis de correspondencia
        """
        contingency_table, lang_coords, word_coords = self.perform_correspondence_analysis()
        
        fig = go.Figure()
        
        # Agregar puntos de idiomas
        fig.add_trace(go.Scatter(
            x=lang_coords[:, 0],
            y=lang_coords[:, 1],
            mode='markers+text',
            text=self.languages,
            textposition='top center',
            marker=dict(size=12, color='#FF6B6B'),
            textfont=dict(color='#FFFFFF', size=12),
            name='Idiomas'
        ))
        
        # Agregar puntos de palabras (muestra limitada)
        sample_words = self.common_words[:5]  # Mostrar solo 5 palabras para claridad
        sample_coords = word_coords[:len(sample_words)]
        
        fig.add_trace(go.Scatter(
            x=sample_coords[:, 0],
            y=sample_coords[:, 1],
            mode='markers+text',
            text=sample_words,
            textposition='bottom center',
            marker=dict(size=8, color='#4ECDC4'),
            textfont=dict(color='#FFFFFF', size=10),
            name='Palabras'
        ))
        
        fig.update_layout(
            title=dict(
                text='Análisis de Correspondencia - Idiomas y Palabras',
                font=dict(size=18, color='#FFFFFF', family='Arial'),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text='Dimensión 1', font=dict(size=16, color='#FFFFFF', family='Arial')),
                tickfont=dict(size=14, color='#FFFFFF', family='Arial'),
                linecolor='#FFFFFF',
                linewidth=3,
                gridcolor='#444444',
                gridwidth=2,
                showgrid=True,
                zeroline=True,
                zerolinecolor='#FFFFFF',
                zerolinewidth=3
            ),
            yaxis=dict(
                title=dict(text='Dimensión 2', font=dict(size=16, color='#FFFFFF', family='Arial')),
                tickfont=dict(size=14, color='#FFFFFF', family='Arial'),
                linecolor='#FFFFFF',
                linewidth=3,
                gridcolor='#444444',
                gridwidth=2,
                showgrid=True,
                zeroline=True,
                zerolinecolor='#FFFFFF',
                zerolinewidth=3
            ),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            width=800,
            height=600,
            showlegend=True,
            legend=dict(
                font=dict(color='#FFFFFF', family='Arial', size=12),
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='#FFFFFF',
                borderwidth=1
            ),
            font=dict(color='#FFFFFF', family='Arial')
        )
        
        return fig
    
    def create_statistical_summary_table(self) -> pd.DataFrame:
        """
        Crea una tabla resumen con estadísticas no paramétricas relevantes para señas.
        
        Returns:
            DataFrame con estadísticas por idioma enfocadas en análisis no paramétrico
        """
        df = self.get_common_words_data()
        
        if df.empty:
            return pd.DataFrame()
        
        # Estadísticas no paramétricas más relevantes para instrucciones de señas
        summary_data = []
        
        for language in self.languages:
            lang_data = df[df['idioma'] == language]['longitud']
            
            if len(lang_data) > 0:
                # Estadísticas no paramétricas
                stats_dict = {
                    'Idioma': language,
                    'Cantidad': len(lang_data),
                    'Mediana': lang_data.median(),
                    'Q1 (Percentil 25)': lang_data.quantile(0.25),
                    'Q3 (Percentil 75)': lang_data.quantile(0.75),
                    'Rango Intercuartílico': lang_data.quantile(0.75) - lang_data.quantile(0.25),
                    'Mínimo': lang_data.min(),
                    'Máximo': lang_data.max(),
                    'Rango': lang_data.max() - lang_data.min(),
                    'Complejidad Promedio': 'Baja' if lang_data.median() < 100 else 'Media' if lang_data.median() < 150 else 'Alta'
                }
                summary_data.append(stats_dict)
        
        if not summary_data:
            return pd.DataFrame()
            
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.set_index('Idioma')
        
        # Redondear valores numéricos
        numeric_columns = summary_df.select_dtypes(include=[np.number]).columns
        summary_df[numeric_columns] = summary_df[numeric_columns].round(2)
        
        return summary_df
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Genera un reporte completo del análisis comparativo.
        
        Returns:
            Diccionario con todos los resultados del análisis
        """
        report = {
            'basic_stats': self.create_statistical_summary_table(),
            'correlation_spearman': self.calculate_spearman_correlation(),
            'correlation_kendall': self.calculate_kendall_tau(),
            'statistical_tests': self.perform_statistical_tests(),
            'association_coefficients': self.calculate_association_coefficients(),
            'common_words': self.common_words,
            'languages': self.languages,
            'data_summary': self.get_common_words_data().describe()
        }
        
        return report


def get_comparative_analyzer(database: SignsDatabase) -> ComparativeAnalyzer:
    """
    Función de utilidad para obtener una instancia del analizador comparativo.
    
    Args:
        database: Base de datos de señas
        
    Returns:
        Instancia de ComparativeAnalyzer
    """
    return ComparativeAnalyzer(database)