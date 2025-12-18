import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import pathlib
import os
import pickle # <--- IMPORTANTE: Para guardar la lista de nombres

# ======================================================
# 1. CONFIGURACIÓN DE HARDWARE
# ======================================================
print("🔍 Verificando aceleración...")
# Nota: En Python 3.11 + Windows, TensorFlow usa CPU por defecto.
# Optimizamos el uso de la CPU para que vaya rápido.
tf.config.optimizer.set_jit(True) # XLA compilation (Acelera CPU)

# ======================================================
# 2. RUTA DE LAS FOTOS
# ======================================================
# Asegúrate que esta ruta sea la correcta en tu PC
data_dir = pathlib.Path(r"C:\Users\PC NITRO\Desktop\Agrosense\archive (1)\New Plant Diseases Dataset(Augmented)\New Plant Diseases Dataset(Augmented)\train")

# ======================================================
# 3. PREPARACIÓN DE DATOS
# ======================================================
img_height = 128
img_width = 128
batch_size = 32 

print("\n📂 Cargando y procesando dataset...")

train_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
num_classes = len(class_names)
print(f"\n🌱 Clases encontradas: {num_classes}")

# --- GUARDADO AUTOMÁTICO DE LA LISTA (SOLUCIÓN DEFINITIVA) ---
print("📝 Guardando lista de nombres en 'nombres_clases.pkl'...")
with open('nombres_clases.pkl', 'wb') as f:
    pickle.dump(class_names, f)
print("✅ Lista guardada. Tu App ya no confundirá frutas.")

# Optimización de carga (Cache en RAM)
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ======================================================
# 4. ARQUITECTURA "PRO"
# ======================================================
model = Sequential([
  # Data Augmentation
  layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
  layers.RandomRotation(0.1),
  layers.RandomZoom(0.1),
  layers.RandomContrast(0.1), # Añadido: Cambia contraste para ser más robusto
  layers.Rescaling(1./255),
  
  # Bloques Convolucionales
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  
  layers.Conv2D(128, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  
  layers.Conv2D(256, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  
  # Clasificación
  layers.Flatten(),
  layers.Dense(256, activation='relu'),
  layers.Dropout(0.5), 
  layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

# ======================================================
# 5. ENTRENAMIENTO INTELIGENTE
# ======================================================
print("\n🔥 INICIANDO ENTRENAMIENTO (GIMNASIO NEURONAL)...")
print("   (Esto puede tardar 20-40 mins en CPU. Paciencia, vale la pena)")

# Aumentamos épocas para que aprenda texturas sutiles (Tomate vs Fresa)
epochs = 25 

# CALLBACKS: Herramientas para guardar solo lo mejor
callbacks = [
    # Guarda el modelo SOLO si es mejor que el anterior
    ModelCheckpoint(
        filepath='modelo_plantas_samsung.keras',
        save_best_only=True,
        monitor='val_accuracy',
        mode='max',
        verbose=1
    ),
    # Si pasan 5 épocas sin mejorar, se detiene para no perder tiempo
    EarlyStopping(
        monitor='val_accuracy',
        patience=5,
        restore_best_weights=True
    )
]

history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs,
  callbacks=callbacks # Activamos los callbacks
)

# ======================================================
# 6. REPORTE FINAL
# ======================================================
print("\n🎉 ¡Entrenamiento finalizado!")
print("💾 El mejor modelo se guardó automáticamente como 'modelo_plantas_samsung.keras'")

# Generar gráfica de rendimiento
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs_range = range(len(acc)) # Se ajusta si paró antes (early stopping)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Precisión Entrenamiento')
plt.plot(epochs_range, val_acc, label='Precisión Validación')
plt.legend(loc='lower right')
plt.title('Precisión (Accuracy)')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Error Entrenamiento')
plt.plot(epochs_range, val_loss, label='Error Validación')
plt.legend(loc='upper right')
plt.title('Error (Loss)')
plt.show()