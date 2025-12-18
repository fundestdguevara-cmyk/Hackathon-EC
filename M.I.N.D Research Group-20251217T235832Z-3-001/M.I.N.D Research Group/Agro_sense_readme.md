# AgroSense+ Pro

**AgroSense Pro** es una aplicación web (Streamlit) de diagnóstico agronómico basada en un modelo de clasificación por imágenes. El agricultor sube la foto de una hoja y la IA devuelve: diagnóstico (enfermedad/plaga), traducción al español, grado de confianza y recomendaciones prácticas de manejo.

---

## 🔎 Características principales

- Carga inteligente de lista de clases (`nombres_clases.pkl`) con respaldo si no existe.
- Interfaz web con Streamlit: subida de imagen, vista previa, botón de análisis y detalle técnico.
- Modelo Keras (`modelo_plantas_samsung.keras`) cargado con `@st.cache_resource` para eficiencia.
- Diccionarios de **traducciones** y **recomendaciones** en español para interpretar la predicción.
- Barra de progreso y mensajes condicionados por el nivel de confianza (éxito/advertencia/error).

---

## 🚀 Requisitos

- Python 3.8 o superior
- Recomendado: entorno virtual

Paquetes principales (ejemplo `requirements.txt`):

```
streamlit
tensorflow
numpy
pillow
scikit-learn
protobuf
```

> Nota: en el código se fuerza el uso de CPU con `os.environ['CUDA_VISIBLE_DEVICES'] = '-1'`. Si quieres usar GPU, elimina o comenta esa línea y configura CUDA/cuDNN correctamente.

---

## 📁 Estructura de archivos (sugerida)

```
AgroSense/
├─ app.py                      # Tu archivo Streamlit (el código)
├─ modelo_plantas_samsung.keras
├─ nombres_clases.pkl
├─ requirements.txt
├─ README.md
└─ assets/
   └─ icon.png
```

---

## ⚙️ Configuración rápida

1. Crear y activar un entorno virtual:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar la app:

```bash
streamlit run app.py
```

La aplicación abrirá un servidor local (por ejemplo `http://localhost:8501`).

---

## 🧠 Recomendaciones sobre el modelo y las clases

- `modelo_plantas_samsung.keras` debe ser un modelo Keras guardado con `model.save(...)` y compatible con `tf.keras.models.load_model`.
- `nombres_clases.pkl` es un archivo pickle que contiene una lista en orden exacto de las clases que el modelo devuelve (índice 0 -> clase 0). Puedes generarlo así:

```python
import pickle
class_names = ['Tomato___healthy', 'Tomato___Bacterial_spot', ...]
with open('nombres_clases.pkl', 'wb') as f:
    pickle.dump(class_names, f)
```

- Si el modelo predice un índice fuera de rango, la app muestra un error y previene fallos.

---

## 🗣️ Traducciones y recomendaciones

- Los diccionarios `traducciones` y `recomendaciones` están definidos dentro del código para mapear la etiqueta en inglés a una descripción en español y a pasos de manejo.
- Para mantener la app robusta, añade claves exactas que coincidan con `nombres_clases.pkl`.

Ejemplo para añadir una nueva entrada:

```python
traducciones['New_Class_Name'] = 'Descripción en Español'
recomendaciones['New_Class_Name'] = 'Pasos de manejo para esta enfermedad o plaga.'
```

---

## 🧪 Preprocesamiento de imagen

- La app redimensiona la imagen a 128x128 píxeles antes de pasarla al modelo:

```python
img = image.resize((128, 128))
img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)
```

- Asegúrate de que tu modelo fue entrenado con el mismo tamaño y orden de canales (RGB) y normalización (si aplicas `x/255.0` durante entrenamiento, deberías replicarlo aquí).

---

## 🛠️ Mejora y reentrenamiento

- Para mejorar precisión: recolecta imágenes etiquetadas de mayor variedad de condiciones (diferentes iluminación, ángulos, estadios de la enfermedad).
- Usa augmentación (rotaciones, flips, cambios de brillo) durante entrenamiento.
- Reentrena el modelo y guarda con el mismo nombre o actualiza la ruta en el código.

---

## 🐞 Solución de problemas comunes

- **app no carga el modelo**: Verifica que `modelo_plantas_samsung.keras` exista y que la versión de TensorFlow sea compatible.
- **predicciones erráticas**: Confirma que el preprocesamiento (resizing y normalización) coincide con el entrenamiento.
- **`nombres_clases.pkl` no encontrado**: La app usa una lista de respaldo, pero es mejor exportar la lista real para mantener concordancia con el modelo.

---

## 🔐 Licencia

Proyecto bajo licencia **MIT**. Haz lo que quieras con el código pero reconoce la autoría y mantén un poco de decencia científica.

---

## 👥 Créditos y contacto

Desarrollado por el equipo de AgroSense. Para mejoras, reportes o datos adicionales contáctanos en el repositorio o responde a este README.

---

## ✅ Notas finales (para desarrolladores)

- Si piensas desplegar en producción: agrega validación de entradas, límites de tamaño de archivo, autenticación y logging.
- Considera añadir un endpoint para enviar imágenes y recibir JSON con diagnóstico (para integrarlo con apps móviles o sistemas de riego automatizados).


