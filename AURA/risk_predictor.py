import joblib
import numpy as np
from pesos_entrenamiento import pesos, bias, media, des_estandar

# funcion sigmoide para la predicción de la neurona
def _sigmoide(z):
    return 1 / (1 + np.exp(-z))

# función para predecir el riesgo 
def predecir_riesgo(paciente, model_path):
    modelo = joblib.load(model_path)

    X = np.array([[paciente["age"], paciente["ejection_fraction"],
        paciente["serum_creatinine"], paciente["serum_sodium"]]])

    return float(modelo.predict_proba(X)[0, 1])


def predecir_riesgo_neurona(paciente):
    x = np.array([paciente["age"], paciente["ejection_fraction"],
        paciente["serum_creatinine"], paciente["serum_sodium"] / 4])

    x_norm = (x - media) / des_estandar
    z = np.dot(x_norm, pesos) + bias
    return float(_sigmoide(z))
