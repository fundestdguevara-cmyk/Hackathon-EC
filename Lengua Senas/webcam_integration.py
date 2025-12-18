import cv2
import mediapipe as mp
import numpy as np
import joblib
import os

class SignLanguagePredictor:
    def __init__(self, model_path="webcam_dataset/modelo_senas.pkl"):
        self.model = None
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.load_model(model_path)
        
        # Historial para suavizado
        self.pred_hist = []
        self.HIST_SIZE = 7

    def load_model(self, path):
        if os.path.exists(path):
            try:
                self.model = joblib.load(path)
                print(f"Modelo cargado desde {path}")
            except Exception as e:
                print(f"Error cargando modelo: {e}")
                self.model = None
        else:
            print(f"Modelo no encontrado en {path}")
            self.model = None

    def landmarks_to_vec(self, hand_landmarks):
        return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark],
                        dtype=np.float32).flatten()

    def get_label(self, handedness):
        return handedness.classification[0].label

    def process_frame(self, frame):
        """
        Procesa un frame de video, detecta manos y realiza predicción.
        Retorna el frame anotado y el texto de la predicción.
        """
        # Voltear horizontalmente para efecto espejo
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)

        left_vec = np.zeros(63, dtype=np.float32)
        right_vec = np.zeros(63, dtype=np.float32)
        num_hands = 0
        prediction_text = ""

        if res.multi_hand_landmarks and res.multi_handedness:
            num_hands = len(res.multi_hand_landmarks)

            for handLms, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
                # Dibujar landmarks
                self.mp_draw.draw_landmarks(frame, handLms, self.mp_hands.HAND_CONNECTIONS)

                vec = self.landmarks_to_vec(handLms)
                label = self.get_label(handed)

                if label == "Left":
                    left_vec = vec
                else:
                    right_vec = vec

        # Si hay modelo cargado y al menos una mano, predecir
        if self.model and num_hands >= 1:
            # Vector fijo 126
            x = np.concatenate([left_vec, right_vec]).reshape(1, -1)
            
            try:
                pred = self.model.predict(x)[0]
                
                # Suavizado
                self.pred_hist.append(pred)
                if len(self.pred_hist) > self.HIST_SIZE:
                    self.pred_hist.pop(0)
                
                prediction_text = max(set(self.pred_hist), key=self.pred_hist.count)
            except Exception as e:
                prediction_text = "Error predicción"
                print(f"Error en predicción: {e}")
        
        return frame, prediction_text, num_hands
