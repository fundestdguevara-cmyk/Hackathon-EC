import cv2
import mediapipe as mp
import numpy as np
import joblib

# ====== Cargar modelo (entrenado con 126 features) ======
model = joblib.load("modelo_senas.pkl")

# ====== MediaPipe (ligero y rápido) ======
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ====== Cámara (Windows) ======
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la cámara.")

def landmarks_to_vec(hand_landmarks):
    return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark],
                    dtype=np.float32).flatten()

def get_label(handedness):
    return handedness.classification[0].label  # "Left" / "Right"

# Suavizado simple: mayoría en una ventana corta (reduce parpadeo)
pred_hist = []
HIST = 7

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    left_vec = np.zeros(63, dtype=np.float32)
    right_vec = np.zeros(63, dtype=np.float32)
    num_hands = 0

    if res.multi_hand_landmarks and res.multi_handedness:
        num_hands = len(res.multi_hand_landmarks)

        for handLms, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            vec = landmarks_to_vec(handLms)
            label = get_label(handed)

            if label == "Left":
                left_vec = vec
            else:
                right_vec = vec

    # Vector fijo 126, igual que en entrenamiento
    x = np.concatenate([left_vec, right_vec]).reshape(1, -1)

    # Solo predecir si hay al menos 1 mano (evita basura)
    if num_hands >= 1:
        pred = model.predict(x)[0]
        pred_hist.append(pred)
        if len(pred_hist) > HIST:
            pred_hist.pop(0)

        # mayoría (suaviza)
        pred_suave = max(set(pred_hist), key=pred_hist.count)

        cv2.putText(frame, pred_suave, (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 0), 3)

    cv2.putText(frame, f"manos:{num_hands}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Signify Vision Prototype", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()