# 🏭 Samsung Merquio - Supply Chain Analytics

Sistema de análisis predictivo para cadena de suministro que utiliza Machine Learning para segmentación de clientes, detección de anomalías, predicción de churn y análisis geográfico.

## 📊 Características Principales

### 👥 **Análisis de Clientes**
- **Detección de Anomalías**: Uso de Isolation Forest para identificar clientes atípicos
- **Clustering K-Prototypes**: Segmentación de clientes en 3 grupos (VIP, Regular, Ocasional)
- **Clasificación Predictiva**: Random Forest para predecir categoría de nuevos clientes

### 🌍 **Análisis Geográfico**
- **Predicción por Región**: Random Forest para predecir región basado en coordenadas
- **Mapas Interactivos**: Visualización geográfica de ventas y distribución
- **Análisis por País/Estado/Ciudad**: Segmentación territorial detallada

### 📈 **Predicción de Churn**
- **Gradient Boosting**: Modelo para predecir riesgo de abandono de clientes
- **Segmentación por Valor**: Clasificación en VIP, Potencial y Estándar
- **Recomendaciones Personalizadas**: Estrategias de retención basadas en riesgo

## 🚀 Instalación y Ejecución

### 1. Prerrequisitos
```bash
# Python 3.8+
# pip o conda
```

### 2. Clonar e Instalar Dependencias
```bash
git clone <repositorio_name>
cd project_main

# Con pip
pip install -r requirements.txt

# Con conda
conda create -n samsung_merquio python=3.14
conda activate samsung_merquio
pip install -r requirements.txt
```

### 3. Instalación de Librerías Específicas
```bash
# Librerías ML
pip install scikit-learn kmodes

# Visualización
pip install plotly matplotlib seaborn

# Análisis de datos
pip install pandas numpy

# Framework web
pip install streamlit

# Descarga de datos
pip install gdown
```

### 4. Pre-cálculo de Clusters (IMPORTANTE)
```bash
# Ejecutar una sola vez (puede tardar varios minutos)
python precompute_clusters.py
```

### 5. Ejecutar la Aplicación
```bash
streamlit run app.py
```

## 📁 Estructura del Proyecto
```
project_main/
├── app.py                          # Aplicación principal Streamlit
├── precompute_clusters.py          # Script para pre-cálculo de clusters
├── requirements.txt                # Dependencias
├── README.md                       # Este archivo
│
├── ml/                            # Modelos de Machine Learning
│   ├── anomaly_detection.py       # Isolation Forest
│   ├── clustering.py             # K-Prototypes
│   ├── customer_classifier.py    # Clasificación de clientes
│   ├── geo_classifier.py         # Clasificación geográfica
│   └── churn_predictor.py        # Predicción de churn
│
├── data/                          # Manejo de datos
│   ├── data_loader.py            # Carga de dataset
│   └── data_processor.py         # Procesamiento
│
├── components/                    # Componentes Streamlit
│   ├── sidebar.py                # Navegación lateral
│   ├── dashboard.py              # Dashboard principal
│   ├── customer_analytics.py     # Análisis de clientes
│   ├── geo_analytics.py          # Análisis geográfico
│   └── churn_analytics.py        # Análisis de churn
│
├── utils/                         # Utilidades
│   ├── config.py                 # Configuración
│   └── visualizations.py         # Funciones de visualización
│
└── assets/                       # Recursos
    └── styles.css               # Estilos CSS
```

## 🎯 Guía de Uso

### Paso 1: Cargar Datos
1. Navega a "Análisis de Clientes"
2. Haz clic en "📥 Cargar y Procesar Datos"
3. Selecciona "Usar clusters pre-computados" para máxima velocidad

### Paso 2: Clasificación de Clientes

#### **Clientes VIP (👑)** 
- **Características**: Alto beneficio por orden (>$1000), alta frecuencia de compra, bajo descuento
- **Ejemplo**: Beneficio: $1500, Ventas: $5000, Descuento: 8%, Pedidos: 10+

#### **Clientes Regulares (⭐)**
- **Características**: Beneficio moderado, frecuencia estable, descuento promedio
- **Ejemplo**: Beneficio: $500, Ventas: $2000, Descuento: 15%, Pedidos: 5-10

#### **Clientes Ocasionales (🛍️)**
- **Características**: Bajo beneficio, compras infrecuentes, alto descuento
- **Ejemplo**: Beneficio: $100, Ventas: $500, Descuento: 25%, Pedidos: <5

### Paso 3: Predicción Geográfica

#### **Clasificación por Región**
El sistema predice la región basándose en:
- Coordenadas (Latitud/Longitud)
- Información demográfica
- Patrones de compra históricos

#### **Cómo usar:**
1. Navega a "Análisis Geográfico"
2. Selecciona nivel (Región, País, Estado, Ciudad)
3. Explora mapas interactivos y estadísticas

### Paso 4: Predicción de Churn

#### **Segmentos de Clientes:**
- **🥇 VIP (Alto Valor)**: Top 20% en ventas totales
- **🥈 Potencial**: 20-50% en ventas totales
- **🥉 Estándar**: Resto de clientes

#### **Niveles de Riesgo:**
- **🟢 Bajo (<40%)**: Cliente saludable
- **🟡 Moderado (40-70%)**: Monitorear
- **🔴 Alto (>70%)**: Acción inmediata requerida

## 🔧 Configuración Avanzada

### Parámetros de Modelos

#### **K-Prototypes (Clustering)**
```python
n_clusters = 3        # VIP, Regular, Ocasional
init = "Cao"          # Método de inicialización
random_state = 13     # Reproducibilidad
```

#### **Isolation Forest (Anomalías)**
```python
contamination = 0.07  # 7% de clientes como anomalías
random_state = 13
```

#### **Gradient Boosting (Churn)**
```python
n_estimators = 200
learning_rate = 0.05
max_depth = 4
```

### Optimización de Rendimiento

#### **Para datasets grandes:**
1. Usar siempre clusters pre-computados
2. Reducir `n_estimators` en modelos
3. Utilizar muestreo estratificado

#### **Comando para actualizar clusters:**
```bash
# Si cambian los datos o parámetros
python update_clusters.py
```

## 📊 Interpretación de Resultados

### Matriz de Clasificación de Clientes
```
Cluster 0 (👑 VIP):     Alto beneficio, baja sensibilidad a descuentos
Cluster 1 (🛍️ Ocasional): Bajo beneficio, alta sensibilidad a descuentos  
Cluster 2 (⭐ Regular):    Beneficio moderado, comportamiento estable
```

### Métricas de Modelos
- **Accuracy**: Proporción de predicciones correctas
- **AUC Score**: Capacidad de distinguir entre clases (0.5=random, 1=perfecto)
- **Precision/Recall**: Balance entre falsos positivos/negativos

## 🐛 Solución de Problemas

### Error: "K-Prototypes muy lento"
- Usar datos pre-computados (`precompute_clusters.py`)
- Reducir tamaño del dataset con muestreo
- Aumentar `verbose=0` para menos output

## 📈 Casos de Uso Empresarial

### 1. **Retención de Clientes VIP**
- Identificar VIP en riesgo de churn
- Ofertas personalizadas
- Atención prioritaria

### 2. **Optimización de Inventario**
- Análisis geográfico de demanda
- Previsión por región
- Distribución eficiente

### 3. **Estrategias de Precio**
- Segmentación por sensibilidad a descuentos
- Precios dinámicos por región
- Promociones dirigidas

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Reconocimientos

- Dataset: DataCo Supply Chain Dataset
- Librerías: Scikit-learn, K-modes, Streamlit
- Algoritmos: Isolation Forest, K-Prototypes, Gradient Boosting

---

### 📋 **Quick Start Cheat Sheet**

```bash
# 1. Instalar
git clone <repo> && cd project_main
pip install -r requirements.txt

# 2. Pre-calcular
python precompute_clusters.py

# 3. Ejecutar
streamlit run app.py

# 4. Navegar
#   1. Análisis de Clientes → Cargar datos
#   2. Ver clusters (VIP/Regular/Ocasional)
#   3. Clasificar nuevo cliente
#   4. Análisis Geográfico → Mapas
#   5. Predicción Churn → Riesgo & Recomendaciones
```

### 🎯 **Ejemplos Rápidos de Clasificación**

| Tipo | Beneficio | Ventas | Descuento | Pedidos | Resultado |
|------|-----------|--------|-----------|---------|-----------|
| VIP | $1500+ | $5000+ | <10% | 10+ | 👑 CLIENTE VIP |
| Regular | $300-800 | $1000-3000 | 10-20% | 5-10 | ⭐ CLIENTE REGULAR |
| Ocasional | <$300 | <$1000 | >20% | <5 | 🛍️ CLIENTE OCASIONAL |