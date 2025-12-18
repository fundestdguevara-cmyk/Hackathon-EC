import numpy as np
import os
from sklearn.neighbors import KNeighborsClassifier
import joblib

DATA_DIR = "dataset_senas"

X = []
y = []

for label in os.listdir(DATA_DIR):
    folder = os.path.join(DATA_DIR, label)
    for file in os.listdir(folder):
        data = np.load(os.path.join(folder, file))
        X.append(data)
        y.append(label)

X = np.array(X)
y = np.array(y)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X, y)

joblib.dump(model, "modelo_senas.pkl")
print("Modelo guardado como modelo_senas.pkl")