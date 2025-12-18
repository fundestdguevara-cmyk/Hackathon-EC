# Sistema de Procesamiento y Predicción — Reserva Puyucunapi

## Resumen
Este repositorio contiene un sistema para el procesamiento y predicción de imágenes tomadas en la Reserva Puyucunapi (afueras de Nanegalito, provincia de Pichincha, Ecuador). El objetivo es automatizar la extracción de recortes útiles a partir de imágenes, aplicar preprocesamiento y ejecutar modelos de inferencia para generar predicciones sobre fauna/objetos detectados.

La colección de scripts y pipelines cubre desde el preprocesamiento y generación de crops hasta la inferencia con modelos guardados en `MODELS/` y la generación de resultados en `RESULTS/`.

## Contrato (inputs / outputs)
- Inputs:
  - Carpeta de imágenes sin procesar (`DATASET_PRUEBA/`).
  - Modelos entrenados en `MODELS/` (ej. `best_mlp_model.pth`, ViT checkpoint).
  - Configuración/archivos auxiliares en `PROCESSING/`.
- Outputs:
  - Archivos de predicción CSV en `RESULTS/predicciones.csv`.
  - Imágenes recortadas procesadas en `RESULTS/crops_clahe/`.
  - Ficheros JSON de resultados de detector en `RESULTS/`.

## Estructura del repositorio (resumen)
- `GUI_model.py` — interfaz  principal 
- `run_pipeline.sh` — script para ejecutar pipeline completo.(No se debe usar porque GUI_model.py ya lo ejecuta)
- `prediction_pipeline.py` — orquesta pasos de predicción e inferencia.
- `Inferencia.py` — utilidades o wrapper para ejecutar inferencia con un modelo.
- `PROCESSING/` — scripts de preprocesamiento (CLAHE, dividir imágenes, extracción de crops, reducción de dimensiones, etc.):
  - `clahe.py`, `divide.py`, `make_crops.py`, `remove_footer.py`, `reduction_vit.py`, `megadetector_step.py`.
- `MODELS/` — pesos y checkpoints (ej. `best_mlp_model.pth`, `deepfaune-vit*.pt`).Toma en cuenta que debes descargar el modelo deepfaune-vit,el link está dentro del archivo .txt
- `RESULTS/` — salidas y predicciones.
- `DATASET_PRUEBA/` — variantes del dataset de ejemplo/prueba.
- `FINE_TUNNING_MLP/` — notebooks y procesos para afinamiento de modelos.
- `AUXILIAR_NOTEBOOKS/` — notebooks de apoyo (slicing, lectura de predicciones).

> Nota: Ajusta las rutas en los scripts si trabajas con rutas absolutas diferentes.

## Requisitos
Instala dependencias listadas en `requirements.txt` (revisar y pinnear versiones si es necesario):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si usas GPU, asegúrate de instalar versiones compatibles de PyTorch (GPU) y las dependencias necesarias.

## Cómo ejecutar (uso rápido)
Para ejecutar todo el sistema (preprocesamiento, extracción de crops, inferencia y generación de resultados) utiliza únicamente `GUI_model.py` — es el punto de entrada que orquesta los pasos necesarios. No es necesario ejecutar `run_pipeline.sh`, `prediction_pipeline.py` ni `Inferencia.py` de forma individual para una corrida estándar; esos scripts se usan sólo para depuración o desarrollo.

Comando mínimo:

```bash
streamlit run GUI_model.py
```


Notas:
- `run_pipeline.sh` sigue incluido en el repositorio para referencia o ejecuciones puntuales, pero no se recomienda usarlo si `GUI_model.py` está disponible y configurado.
- Si necesitas ejecutar pasos por separado (p. ej. depurar la inferencia), usa `Inferencia.py` o `prediction_pipeline.py` conscientemente y revisa sus argumentos.

Revisa los scripts para ver parámetros adicionales (rutas, umbrales, batch sizes) sólo cuando trabajes en depuración o desarrollo.

## Descripción de pipelines
- Preprocesamiento (en `PROCESSING/`):
  - `clahe.py` — mejora contraste local en crops.
  - `make_crops.py` — divide imágenes en recortes o extrae detecciones.
  - `remove_footer.py` — elimina barras/áreas no deseadas.
  - `megadetector_step.py` — paso opcional con MegaDetector para localizar animales/objetos.
- Inferencia (`Inferencia.py`, `prediction_pipeline.py`):
  - Carga modelos en `MODELS/`, procesa crops y genera predicciones guardadas en `RESULTS/`.

## Modelos
- Modelos entrenados/guardados en `MODELS/`.
- Ejemplos encontrados: `best_mlp_model.pth`, checkpoints ViT (`deepfaune-vit*.pt`).
- Si deseas re-entrenar o afinar modelos, usa `FINE_TUNNING_MLP/` y el notebook `fine_tunning.ipynb`.

## Datos
- Carpeta `DATASET_PRUEBA/` 

## Resultados y visualización
- Predicciones: `RESULTS/predicciones.csv`.
- Crops procesados: `RESULTS/crops_clahe/`.
- JSON de detecciones: `RESULTS/resultados_megadetector.json`.


## ZooDataVision Assistant - Chatbot 

En esta sección se explica cómo instalar y ejecutar el **chatbot de ZooDataVision** usando Streamlit y Ollama con el modelo `gemma3:4b`.  
Sigue estos pasos para tener tu asistente de biodiversidad funcionando en minutos.

---

### 1. Requisitos previos

- **Python 3.12+** (recomendado usar Anaconda o venv)
- **Ollama** instalado y corriendo en tu máquina  
  [Descargar Ollama](https://ollama.com/download)
- **Modelo `gemma3:4b` descargado en Ollama**

---

### 2. Instalación de dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

Si no tienes langchain_ollama, instálalo manualmente:

```bash
pip install langchain_ollama
```

### 3. Descargar el modelo Gemma 3 (4b) en Ollama

En la terminal, ejecuta:
```bash
ollama pull gemma3:4b
```

Asegúrate de que Ollama esté corriendo antes de continuar.

### 4. Ejecutar el chatbot con Streamlit (solo chatbot)

Desde la carpeta ``CHATBOT``, ejecuta:
```bash
streamlit run [app.py]
```
Esto abrirá una ventana en tu navegador con la interfaz del chatbot.

### 5. Ejecutar la GUI completa (incluye el chatbot)
Desde la carpeta raíz del proyecto (donde está ``GUI_model.py``), ejecuta:
```bash
streamlit run [GUI_model.py]
```

Esto abrirá la plataforma completa en tu navegador.
Para usar el chatbot, selecciona la pestaña **"Asistente IA (Chatbot)"** en la parte superior.

### 6. Uso del chatbot
- Escribe tus preguntas sobre el dataset de predicciones, por ejemplo:
    - ¿Cuántas aves grandes se detectaron?
    - Dame un resumen estadístico de los resultados

- El chatbot analizará el archivo ``RESULTS/predicciones``.csv y responderá usando RAG (Retrieval Augmented Generation).

- El historial de la conversación se mantiene en pantalla y puedes seguir preguntando.

### 7. Notas importantes

- El archivo RESULTS/predicciones.csv debe existir y estar actualizado para que el chatbot funcione correctamente.
- Si cambias el modelo o la ruta del CSV, actualiza la configuración en el código.
- Si tienes problemas con dependencias, revisa que tu entorno virtual esté activado.