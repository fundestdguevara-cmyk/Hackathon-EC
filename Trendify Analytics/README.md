# 📈 Trendify Analytics — Pronóstico de Ventas

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Plataforma modular de análisis y pronóstico de series temporales con selección automática de modelos estadísticos e integración opcional de IA.**

Desarrollado por **Trendify Analytics** para facilitar la predicción de ventas, demanda y otras métricas temporales con rigor científico y presentación ejecutiva.

---

## 🚀 Características principales

- **📊 Dashboard interactivo web**: Interfaz Streamlit para cargar CSV, configurar parámetros y obtener pronósticos en tiempo real
- **🤖 Selección automática de modelos**: Auto-ARIMA selecciona órdenes óptimas para SARIMA/SARIMAX
- **✅ Validación robusta**: Rolling-origin cross-validation simula despliegue real y evalúa precisión (RMSE, MAE, MAPE)
- **📈 Modelos avanzados**: Seasonal Naive, SARIMA, SARIMAX (con exógenas), Holt-Winters
- **🧠 Explicación con IA (opcional)**: Integración con Hugging Face Inference API para análisis automático
- **📉 Visualizaciones ejecutivas**: Gráficos interactivos (Plotly) con intervalos de confianza, continuidad y variación mensual
- **💾 Exportación completa**: CSV de pronóstico, diagnóstico (histórico+predicción) y reportes
- **📚 Documentación integrada**: Guías de uso, tooltips y explicaciones de métricas/gráficos

---

## 📦 Instalación

### Requisitos previos
- Python 3.11 o superior
- pip o conda

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/trendify-analytics.git
cd trendify-analytics
```

### 2. Crear entorno virtual (recomendado)
```bash
# Con venv
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# O con conda
conda create -n trendify python=3.11
conda activate trendify
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

**Nota sobre SciPy**: Si encuentras errores con `_lazywhere`, asegúrate de tener `scipy==1.10.1` como se especifica en `requirements.txt`.

---

## 🎯 Uso

### Opción 1: Dashboard web (recomendado para usuarios finales)

```bash
streamlit run streamlit_app.py
```

La aplicación se abrirá en tu navegador (por defecto `http://localhost:8501`).

**Flujo de trabajo:**
1. **Carga tu CSV**: Archivo con columna de fechas y al menos una columna numérica (ventas, demanda, etc.)
   - Ejemplo de estructura:
     ```csv
     fecha,ventas,producto_a,producto_b
     2022-01-01,6545.72,1200,850
     2022-02-01,8374.50,1450,920
     ```
2. **Configura parámetros**:
   - Horizonte de pronóstico: 3-12 meses
   - Longitud estacional: 12 para datos mensuales con ciclo anual
   - Ventana inicial CV: 24+ para validación robusta
   - HF_TOKEN (opcional): Para análisis con IA
3. **Ejecuta análisis**: Haz clic en "Ejecutar análisis y pronóstico"
4. **Revisa resultados**:
   - Órdenes auto-ARIMA
   - Métricas de validación cruzada
   - Gráficos de pronóstico con IC 95%
   - Plan de acción sugerido
   - Explicación IA (si token provisto)
5. **Descarga CSVs**: Pronóstico y diagnóstico para análisis posterior

### Opción 2: Notebooks (para análisis profundo)

Usa los notebooks Jupyter para exploración detallada:
- `project_ia_final.ipynb`: Notebook completo con EDA, feature engineering, SARIMAX, CV, visualizaciones profesionales y reportes
- `project_ia.ipynb`: Notebook original con análisis exploratorio

```bash
jupyter notebook
# Abre project_ia_final.ipynb
```

**Contenido del notebook final:**
- Resumen ejecutivo
- EDA riguroso (descomposición, ACF/PACF, ADF)
- Feature engineering (exógenas simuladas: temperatura, dummies)
- Auto-ARIMA para SARIMA y SARIMAX
- Rolling-origin CV con 4 modelos
- Pronóstico H1 2025 con IC
- Análisis de residuos
- Conclusiones y recomendaciones

---

## 📂 Estructura del proyecto

```
trendify-analytics/
├── streamlit_app.py              # Dashboard web interactivo
├── project_ia_final.ipynb        # Notebook completo (recomendado)
├── project_ia.ipynb              # Notebook exploratorio original
├── requirements.txt              # Dependencias Python
├── ventas_m.csv                  # Dataset ejemplo (2022-2024)
├── diagnostico_pronostico_2025.csv  # Output de ejemplo
└── README.md                     # Esta documentación
```

---

## 🛠️ Tecnologías

### Core
- **Python 3.11**: Lenguaje principal
- **Streamlit 1.32**: Framework web para dashboards interactivos
- **Pandas 2.2**: Manipulación de datos
- **NumPy 1.26**: Operaciones numéricas

### Modelado y estadística
- **statsmodels 0.14**: SARIMAX, Holt-Winters, pruebas ADF
- **pmdarima 2.0**: Auto-ARIMA para selección automática de órdenes
- **scikit-learn 1.3**: Métricas (RMSE, MAE)

### Visualización
- **Plotly 5.18**: Gráficos interactivos con zoom/hover
- **Matplotlib 3.8**: Gráficos estáticos
- **Seaborn 0.13**: Heatmaps y visualizaciones estadísticas

### IA (opcional)
- **Hugging Face Inference API**: Análisis automático con LLMs gratuitos (Mixtral-8x7B)
- **requests**: Llamadas HTTP a la API

---

## 🔑 Configuración de Hugging Face (opcional)

Para habilitar la explicación automática con IA:

1. Crea una cuenta gratuita en [huggingface.co](https://huggingface.co)
2. Genera un token en [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. En el dashboard, ingresa el token en el campo "HF_TOKEN de Hugging Face"

**Modelos usados**: `mistralai/Mixtral-8x7B-Instruct-v0.1` (gratuito vía Inference API)

---

## 📊 Ejemplo de caso de uso

### Contexto
Una heladería quiere pronosticar ventas de enero–junio 2025 para:
- Planificar inventario de ingredientes
- Ajustar staffing en meses pico
- Diseñar campañas pre-verano

### Datos
36 meses de historia (2022-2024) con ventas totales y por producto.

### Proceso
1. Carga `ventas_m.csv` en el dashboard
2. Configura horizonte=6, estacional=12, ventana=24
3. Ejecuta análisis
4. **Resultados**:
   - Modelo seleccionado: SARIMAX (MAPE=8.2%)
   - Picos detectados: enero, marzo, diciembre
   - IC 95%: ±$4,800 promedio
5. **Acción**:
   - Incrementar stock 20% en diciembre
   - Lanzar campaña "Verano Anticipado" en noviembre
   - Contratar personal temporal para enero-marzo

---

## 📈 Métricas y validación

### Métricas de evaluación
- **RMSE** (Root Mean Squared Error): Penaliza errores grandes; útil para detectar outliers
- **MAE** (Mean Absolute Error): Error promedio en unidades originales; fácil interpretación
- **MAPE** (Mean Absolute Percentage Error): Error porcentual; independiente de escala; **métrica principal**

### Rolling-origin cross-validation
Simula despliegue mensual:
- Ventana inicial: 24 meses
- Horizonte de prueba: 3 meses
- Expande incrementalmente para validar robustez

### Selección de modelo
Prioridad con tolerancia de 2% en MAPE:
1. **SARIMAX** (preferido si disponible)
2. **SARIMA**
3. **Holt-Winters**
4. **Seasonal Naive** (línea base)

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Ideas para contribuir
- Soporte para datos diarios/semanales
- Exportación PDF con reportes visuales
- Integración con bases de datos (PostgreSQL, BigQuery)
- Modelos de ML (XGBoost, LSTM)
- Dashboard multi-idioma
- API REST para pronósticos programáticos

---

## 📝 Notas técnicas

### Frecuencias soportadas
- Mensual (MS): Recomendado, probado exhaustivamente
- Otras frecuencias (D, W, Q): Experimentales; ajusta `season_len` manualmente

### Exógenas
- **Simuladas** (notebook): temperatura coseno + dummies enero/diciembre
- **Personalizadas** (dashboard): Selecciona columnas del CSV como exógenas
- **Futuras**: Se extrapolan repitiendo el último ciclo estacional

### Limitaciones conocidas
- Requiere mínimo 24-36 observaciones para validación robusta
- SARIMAX puede fallar con exógenas muy correlacionadas o con nulos
- Inference API de HF tiene límite de rate (free tier: ~1,000 requests/día)

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- **statsmodels** y **pmdarima**: Por herramientas robustas de series temporales
- **Streamlit**: Por facilitar dashboards interactivos en Python
- **Hugging Face**: Por democratizar el acceso a LLMs de código abierto
- **Comunidad de Data Science**: Por compartir conocimiento y mejores prácticas

---

## 📧 Contacto

**Trendify Analytics**  
- Email: contact@trendify-analytics.com (ejemplo)
- GitHub: [@trendify-analytics](https://github.com/trendify-analytics) (ejemplo)
- LinkedIn: [Trendify Analytics](https://linkedin.com/company/trendify-analytics) (ejemplo)

---

## 🔮 Roadmap

- [ ] Soporte para múltiples targets simultáneos
- [ ] Comparación automática de horizontes (1, 3, 6, 12 meses)
- [ ] Detección de outliers y estacionalidad múltiple
- [ ] Integración con Google Sheets / Excel online
- [ ] Deployment en Streamlit Cloud / Heroku / AWS
- [ ] API REST para integración con otros sistemas
- [ ] Dashboard multi-usuario con autenticación

---

**¿Listo para pronosticar con confianza? Ejecuta `streamlit run streamlit_app.py` y comienza ahora. 🚀**
