# 🤖 Asistente Energético Inteligente (ENERGY STAR)

Este proyecto implementa un **asistente energético inteligente en Python** que analiza el consumo eléctrico de un usuario, lo compara con perfiles similares mediante *Machine Learning* (K-Means) y ofrece **recomendaciones reales de modelos ENERGY STAR** para reducir consumo y costos.

Integra:
- 📊 Análisis de datos con **pandas y NumPy**
- 🤖 Clustering con **scikit-learn (KMeans)**
- 📈 Visualización con **Matplotlib**
- 🧠 Generación de análisis y recomendaciones con **Gemini (Google Generative AI)**
- 🔌 Datos reales de certificación **ENERGY STAR**

---

## 📌 Características principales

- Carga **datasets reales de ENERGY STAR** para distintos electrodomésticos.
- Calcula el **consumo promedio mensual** por tipo de aparato.
- Genera un **dataset sintético de usuarios** para entrenamiento.
- Clasifica al usuario en un **cluster de consumo energético**.
- Compara visualmente el consumo del usuario vs su cluster.
- Detecta **consumos elevados** automáticamente.
- Recomienda **modelos reales ENERGY STAR** más eficientes.
- Calcula **ahorro energético (kWh)** y **ahorro económico (USD)**.

---

## 🏠 Electrodomésticos soportados

- Televisores
- Computadoras
- Luminarias
- Ventiladores
- Lavadoras comerciales
- Aires acondicionados
- Refrigeradores comerciales
- Cocinas eléctricas

*(El sistema solo usa los dispositivos cuyos datasets estén disponibles)*

---

## ⚙️ Requisitos

Instala las dependencias necesarias:

```bash
pip install pandas numpy matplotlib scikit-learn google-generativeai python-dotenv
```

---

## 🔑 Configuración de la API de Gemini

En el código se utiliza **Google Gemini** para generar análisis y recomendaciones.

Actualmente la clave se configura directamente:

```python
genai.configure(api_key="TU_API_KEY_AQUI")
```

🔐 **Recomendación:** Usa variables de entorno para mayor seguridad:

```bash
export GEMINI_API_KEY="tu_api_key"
```

Y luego en Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

---

## 📂 Estructura esperada de archivos

Los datasets ENERGY STAR deben estar en la ruta especificada en el código:

```text
/content/
├── ENERGY_STAR_Certified_Televisions_20251217.csv
├── ENERGY_STAR_Certified_Computers_V9.0_20251217.csv
├── ENERGY_STAR_Certified_Light_Fixtures_-_Downlights_20251217.csv
├── ENERGY_STAR_Certified_Ventilating_Fans_20251217.csv
├── ENERGY_STAR_Certified_Commercial_Clothes_Washers_20251217.csv
├── ENERGY_STAR_Certified_Room_Air_Conditioners_20251217.csv
├── ENERGY_STAR_Certified_Commercial_Refrigerators_and_Freezers_20251217.csv
├── ENERGY_STAR_Certified_Commercial_Electric_Cooktops_20251217.csv
```

---

## ▶️ Ejecución del programa

Ejecuta el script principal:

```bash
python main.py
```

El asistente te pedirá el **consumo mensual (kWh)** de cada electrodoméstico disponible.

---

## 📊 Flujo de funcionamiento

1. Carga y limpia datasets ENERGY STAR reales.
2. Calcula consumos anuales y mensuales promedio.
3. Genera usuarios sintéticos para entrenamiento.
4. Entrena un modelo **KMeans (3 clusters)**.
5. Clasifica al usuario según su perfil energético.
6. Visualiza la comparación de consumo.
7. Analiza el perfil con Gemini.
8. Detecta consumos altos.
9. Recomienda modelos reales más eficientes.
10. Calcula ahorro energético y económico.

---

## 📈 Visualización

El sistema genera una gráfica de barras que muestra:

- 🔋 Consumo mensual del usuario
- 📉 Promedio del cluster asignado

Esto permite identificar rápidamente excesos de consumo.

---

## 💡 Ejemplo de recomendaciones

- Modelos ENERGY STAR más eficientes
- Consumo anual estimado
- Ahorro en kWh
- Ahorro económico anual (USD)

---

## 💰 Costo de energía

El costo de energía se define como:

```python
COSTO_KWH = 0.13  # USD/kWh
```

Puedes ajustarlo según tu país o tarifa eléctrica.

---

## 🚀 Posibles mejoras futuras

- Interfaz gráfica (Web o Desktop)
- Exportar reportes en PDF
- Soporte para más electrodomésticos
- Ajuste dinámico de horas de uso
- Conexión con medidores inteligentes
---

## 🧠 Tecnologías utilizadas

- Python 3
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- Google Generative AI (Gemini)
- ENERGY STAR Datasets

---

✨ **Asistente Energético Inteligente** – Reduce consumo, ahorra dinero y cuida el planeta 🌍

