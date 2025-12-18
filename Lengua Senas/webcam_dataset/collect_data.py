import cv2
import mediapipe as mp
import numpy as np
import os
import time

# ================= CONFIGURACIÓN =================
CAM_INDEX = 0
WIDTH, HEIGHT = 640, 480        # baja a 424x240 si tu PC es flojo
PROCESS_EVERY_N = 2             # procesa 1 de cada N frames
INTERVAL_MS = 200               # guardado automático
DRAW_LANDMARKS = True           # False = aún más rápido

# ================= MEDIAPIPE =====================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0,          # MÁS RÁPIDO
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ================= DATASET ======================
DATA_DIR = "dataset_senas"
os.makedirs(DATA_DIR, exist_ok=True)

PALABRA = input("Nombre de la seña: ").strip()
SAVE_DIR = os.path.join(DATA_DIR, PALABRA)
os.makedirs(SAVE_DIR, exist_ok=True)

# ================= CÁMARA =======================
cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la cámara")

# ================= FUNCIONES ====================
def landmarks_to_vec(hand_landmarks):
    return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark],
                    dtype=np.float32).flatten()

def get_label(handedness):
    return handedness.classification[0].label  # Left / Right

# ================= ESTADO =======================
recording = False
count = 0
last_save = 0.0
interval_s = INTERVAL_MS / 1000.0
frame_i = 0

# Mantener último estado válido (evita parpadeo)
last_left = np.zeros(63, dtype=np.float32)
last_right = np.zeros(63, dtype=np.float32)
last_num_hands = 0

# ================= LOOP =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_i += 1

    if frame_i % PROCESS_EVERY_N == 0:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        left_vec = np.zeros(63, dtype=np.float32)
        right_vec = np.zeros(63, dtype=np.float32)
        num_hands = 0

        if res.multi_hand_landmarks and res.multi_handedness:
            num_hands = len(res.multi_hand_landmarks)

            for handLms, handed in zip(res.multi_hand_landmarks,
                                       res.multi_handedness):
                if DRAW_LANDMARKS:
                    mp_draw.draw_landmarks(
                        frame, handLms, mp_hands.HAND_CONNECTIONS
                    )

                vec = landmarks_to_vec(handLms)
                label = get_label(handed)

                if label == "Left":
                    left_vec = vec
                else:
                    right_vec = vec

        # Actualizar SOLO si hay al menos 1 mano
        if num_hands >= 1:
            last_left = left_vec
            last_right = right_vec
            last_num_hands = num_hands
        else:
            last_num_hands = 0

    # Vector final SIEMPRE de tamaño fijo
    sample_vec = np.concatenate([last_left, last_right])

    # ================= GUARDADO ==================
    now = time.time()
    if recording and last_num_hands >= 1 and (now - last_save) >= interval_s:
        np.save(os.path.join(SAVE_DIR, f"{count}.npy"), sample_vec)
        count += 1
        last_save = now

    # ================= UI ========================
    if recording:
        cv2.putText(frame, "REC", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(
        frame,
        f"{PALABRA} | manos:{last_num_hands} | muestras:{count}",
        (10, HEIGHT - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow("Captura de señas (R=REC / Q=Salir)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        recording = not recording
        last_save = 0.0

cap.release()
cv2.destroyAllWindows()