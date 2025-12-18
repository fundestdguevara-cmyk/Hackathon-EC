import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_main_chart(df_filtered, nivel, metrica, top_n):
    """Crear gráfico principal de barras horizontales"""
    # Agrupar datos según la selección
    if nivel == 'Date':
        df_filtered['Date_only'] = df_filtered['Date'].dt.date
        grouped = df_filtered.groupby('Date_only')[metrica].sum().reset_index()
        grouped = grouped.sort_values(by=metrica, ascending=False).head(top_n)
        x_col = 'Date_only'
    elif nivel == 'Time':
        df_filtered['Hour'] = df_filtered['Time'].apply(lambda x: x.hour)
        grouped = df_filtered.groupby('Hour')[metrica].sum().reset_index()
        grouped = grouped.sort_values(by=metrica, ascending=False).head(top_n)
        x_col = 'Hour'
    else:
        grouped = df_filtered.groupby(nivel)[metrica].sum().reset_index()
        grouped = grouped.sort_values(by=metrica, ascending=False).head(top_n)
        x_col = nivel
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Elegir colores según métrica
    if metrica == 'Sales':
        colors = plt.cm.viridis(np.linspace(0, 1, len(grouped)))
        xlabel = 'Ventas Totales ($)'
        title_suffix = "Ventas"
    else:
        colors = plt.cm.plasma(np.linspace(0, 1, len(grouped)))
        xlabel = 'Cantidad Total'
        title_suffix = "Cantidad"
    
    # Crear barras horizontales
    bars = ax.barh(grouped[x_col].astype(str), grouped[metrica], color=colors)
    ax.set_xlabel(xlabel, fontsize=12)
    
    # Configurar título
    if nivel == 'Hour':
        ax.set_ylabel('Hora del día', fontsize=12)
        title = f'Top {top_n} Horas por {title_suffix}'
    else:
        ax.set_ylabel(nivel, fontsize=12)
        title = f'Top {top_n} {nivel} por {title_suffix}'
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Añadir etiquetas de valor
    for bar, value in zip(bars, grouped[metrica]):
        width = bar.get_width()
        if metrica == 'Sales':
            label = f'${value:,.2f}'
        else:
            label = f'{int(value):,}'
        
        ax.text(width + max(grouped[metrica])*0.01,
                bar.get_y() + bar.get_height()/2,
                label, va='center', fontsize=9)
    
    # Estilo
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    return fig

def create_pie_chart(data, labels, title, colormap='Set3'):
    """Crear gráfico de torta"""
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = getattr(plt.cm, colormap)(np.linspace(0, 1, len(data)))
    ax.pie(data, labels=labels, autopct='%1.1f%%', colors=colors)
    ax.set_title(title)
    return fig

def create_bar_chart(categories, values, title, xlabel, ylabel, colors=None):
    """Crear gráfico de barras"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if colors is None:
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    bars = ax.bar(categories, values, color=colors[:len(categories)])
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # Añadir etiquetas
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.01,
                f'{value:,.0f}', ha='center', fontsize=10)
    
    return fig