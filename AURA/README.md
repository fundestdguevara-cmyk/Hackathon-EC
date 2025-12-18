AURA • Predicción de Riesgo Cardiovascular (Python)

Aplicación de escritorio en Python con interfaz gráfica moderna (Tkinter + ttk) para estimar el riesgo cardiovascular a partir de variables clínicas y generar explicaciones/recomendaciones por factor.

Incluye 2 modos de predicción:

Random Forest cargado desde archivo .joblib

Neurona logística basada en pesos entrenados (implementación propia)

Características

Interfaz gráfica moderna con estilo “card” y fondo degradado.

Predicción de riesgo en porcentaje (0–100%).

Clasificación del riesgo: Bajo / Medio / Alto.

Explicación y recomendaciones automáticas por cada variable.

Botón para guardar reporte en .txt.

Selección de modelo .joblib desde la interfaz (Random Forest).

Requisitos

Python 3.9+ (recomendado 3.10 o 3.11)

Librerías:

joblib

numpy

Tkinter normalmente ya viene instalado con Python en Windows.

Instalación
1) Crear entorno (opcional pero recomendado)

Windows (PowerShell):

python -m venv .venv
.\.venv\Scripts\activate


Linux/Mac:

python3 -m venv .venv
source .venv/bin/activate

2) Instalar dependencias
pip install -r requirements.txt


Si no tienes requirements.txt, instala manualmente:

pip install joblib numpy

Estructura del proyecto

Ejemplo recomendado:

AURA/
│── app_gui.py
│── risk_predictor.py
│── factor_explainer.py
│── pesos_entrenamiento.py
│── entrenamiento_neurona.py
│── modelo_random_forest_entrenado.joblib
│── dataset_balanceado_con_smote.csv
│── resultados_modelo_logistico.json
│── README.md
│── requirements.txt

Archivos principales

app_gui.py
Interfaz gráfica (GUI) de la aplicación.

risk_predictor.py
Lógica de predicción:

predecir_riesgo(paciente, model_path) (Random Forest)

predecir_riesgo_neurona(paciente) (Neurona logística)

factor_explainer.py
Genera texto de explicación y recomendaciones por factor:

explicacion_por_cada_factor(paciente)

pesos_entrenamiento.py
Contiene w_age, w_ef, w_crea, w_sodium, bias para la neurona.

modelo_random_forest_entrenado.joblib
Modelo entrenado de Random Forest (formato joblib).

Cómo ejecutar la aplicación

Desde la carpeta del proyecto:

python app_gui.py


Se abrirá la ventana de AURA.
Pasos:

Selecciona el modelo: Random Forest o Neurona.

Ingresa los valores del paciente:

Edad (años)

Fracción de eyección (%)

Creatinina sérica (mg/dL)

Sodio sérico (mEq/L)

Presiona Calcular riesgo.

Revisa el porcentaje, el nivel y las recomendaciones.

(Opcional) Guarda el reporte en txt.

Formato de entrada (paciente)

Internamente se usa un diccionario:

paciente = {
  "age": 60,
  "ejection_fraction": 35,
  "serum_creatinine": 1.2,
  "serum_sodium": 137
}

Modelos y predicción
Random Forest (joblib)

Se carga desde modelo_random_forest_entrenado.joblib.

Puedes cambiar el archivo desde la interfaz con Elegir .joblib.

Neurona logística (pesos)

Usa pesos definidos en pesos_entrenamiento.py.

Aplica estandarización usando medias y desviaciones definidas en risk_predictor.py (o el módulo de entrenamiento).

Recomendación: si ajustas la normalización/estandarización en el entrenamiento, actualiza la misma lógica en risk_predictor.py para mantener consistencia.

Troubleshooting
1) “No se encontró el archivo .joblib”

Asegúrate de que modelo_random_forest_entrenado.joblib esté:

en la misma carpeta que app_gui.py, o

seleccionado manualmente desde el botón Elegir .joblib.

2) Error con Tkinter (Linux)

En algunas distros debes instalarlo:

sudo apt-get install python3-tk

3) Pantalla se ve muy grande/pequeña

Puedes ajustar:

self.geometry("980x600")

self.minsize(930, 560)
en app_gui.py.