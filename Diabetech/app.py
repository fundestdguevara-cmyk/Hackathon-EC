import os
import glob
import numpy as np
import tensorflow as tf
import streamlit as st
from llm import llm_reply

st.set_page_config(page_title="DiabeTech Predict", page_icon="logo.png", layout="wide")
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=200)

with col2:
    st.title("DiabeTech Predict")
    st.caption("Formulario clínico + Predicción real (.keras) + Chat de apoyo (Ollama).")

# =========================
# Dataset schema (real)
# =========================
BIN_FEATURES = [
    ("HighBP", "HighBP (Hipertensión)"),
    ("HighChol", "HighChol (Colesterol alto)"),
    ("CholCheck", "CholCheck (Chequeo colesterol últimos 5 años)"),
    ("Smoker", "Smoker (≥100 cigarrillos en la vida)"),
    ("Stroke", "Stroke (Derrame cerebral previo)"),
    ("HeartDiseaseorAttack", "HeartDiseaseorAttack (Enfermedad coronaria o infarto)"),
    ("PhysActivity", "PhysActivity (Actividad física últimos 30 días)"),
    ("Fruits", "Fruits (Fruta diaria)"),
    ("Veggies", "Veggies (Vegetales diarios)"),
    ("HvyAlcoholConsump", "HvyAlcoholConsump (Alcohol excesivo)"),
    ("AnyHealthcare", "AnyHealthcare (Tiene cobertura de salud)"),
    ("NoDocbcCost", "NoDocbcCost (No vio médico por costo)"),
    ("DiffWalk", "DiffWalk (Dificultad caminar/escaleras)"),
    ("Sex", "Sex (Sexo biológico: 1 Hombre / 0 Mujer)"),
]

NUM_FEATURES = [
    ("BMI", "BMI (Índice de Masa Corporal)", 10.0, 70.0),
    ("MentHlth", "MentHlth (Días mala salud mental: 0–30)", 0, 30),
    ("PhysHlth", "PhysHlth (Días mala salud física: 0–30)", 0, 30),
]

ORD_FEATURES = [
    ("GenHlth", "GenHlth (1=Excelente ... 5=Mala)", 1, 5),
    ("Age", "Age (Categoría 1–14)", 1, 14),
    ("Education", "Education (1–6)", 1, 6),
    ("Income", "Income (1–8)", 1, 8),
]

FEATURE_ORDER = (
    [k for k, _ in BIN_FEATURES]
    + [k for k, *_ in NUM_FEATURES]
    + [k for k, *_ in ORD_FEATURES]
)

# =========================
# Model loading/prediction
# =========================
AVG_MODELS_DIR = os.path.join("server", "nodeC", "models", "avg")


def list_avg_models() -> list[str]:
    paths = glob.glob(os.path.join(AVG_MODELS_DIR, "*.keras"))
    paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return paths


def pick_default_model(paths: list[str]) -> str | None:
    if not paths:
        return None
    for p in paths:
        if os.path.basename(p).lower() != "initial.keras":
            return p
    return paths[0]


@st.cache_resource(show_spinner=False)
def load_keras_model(model_path: str):
    return tf.keras.models.load_model(model_path, compile=False)


def build_input_vector(form_values: dict) -> np.ndarray:
    x = [float(form_values[f]) for f in FEATURE_ORDER]
    return np.array([x], dtype=np.float32)  # (1, 21)


def predict_risk_keras(form_values: dict, model_path: str) -> dict:
    model = load_keras_model(model_path)
    X = build_input_vector(form_values)
    y = model.predict(X, verbose=0)
    y = np.array(y)

    if y.ndim == 2 and y.shape[1] == 1:
        prob = float(y[0, 0])
    elif y.ndim == 2 and y.shape[1] >= 2:
        prob = float(y[0, 1])
    else:
        prob = float(y.flatten()[0])

    pred = 1 if prob >= 0.5 else 0

    if prob < 0.33:
        level = "Bajo"
    elif prob < 0.66:
        level = "Moderado"
    else:
        level = "Elevado"

    return {
        "probability": prob,
        "pred_label": pred,
        "level": level,
        "threshold": 0.5,
        "model_path": model_path,
        "disclaimer": "Esto es informativo y no reemplaza la evaluación de un profesional de la salud.",
    }


# =========================
# Session state
# =========================
if "form" not in st.session_state:
    st.session_state.form = {k: None for k in FEATURE_ORDER}

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hola. Soy DiabeTech Assistant.\n\n"
                "Estoy aquí para ayudarte a:\n"
                "- Entender el significado de las variables del formulario\n"
                "- Saber qué valores ingresar (0/1, rangos)\n"
                "- Explicar cómo interpretar el resultado\n\n"
                "Puedes preguntarme, por ejemplo: “¿Qué significa DiffWalk?”"
            ),
        }
    ]

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_report" not in st.session_state:
    st.session_state.last_report = ""


def validate_form(data: dict) -> list[str]:
    errors = []

    for k, _ in BIN_FEATURES:
        v = data.get(k)
        if v not in (0, 1):
            errors.append(f"{k}: debe ser 0 o 1.")

    for k, _, mn, mx in NUM_FEATURES:
        v = data.get(k)
        if v is None:
            errors.append(f"{k}: es requerido.")
            continue
        try:
            fv = float(v)
            if fv < mn or fv > mx:
                errors.append(f"{k}: fuera de rango ({mn}–{mx}).")
        except Exception:
            errors.append(f"{k}: valor inválido.")

    for k, _, mn, mx in ORD_FEATURES:
        v = data.get(k)
        if v is None:
            errors.append(f"{k}: es requerido.")
            continue
        try:
            iv = int(v)
            if iv < mn or iv > mx:
                errors.append(f"{k}: fuera de rango ({mn}–{mx}).")
        except Exception:
            errors.append(f"{k}: valor inválido (entero).")

    return errors


# =========================
# Layout
# =========================
tab_form, tab_chat = st.tabs(["Formulario clínico", "Chat de apoyo"])

# Formulario
with tab_form:
    st.subheader("Ingreso de datos del paciente")
    st.write(
        "Completa los campos. Luego presiona **Evaluar** para predecir con el modelo global (.keras)."
    )

    # Selector de modelo
    model_paths = list_avg_models()
    default_model = pick_default_model(model_paths)

    if not model_paths:
        st.warning(
            "No encontré modelos en `nodeC/models/avg/*.keras`.\n\n"
            "Primero ejecuta el entrenamiento federado (server) para generar modelos promediados."
        )

    selected_model = st.selectbox(
        "Modelo global a usar (.keras)",
        options=model_paths if model_paths else ["(sin modelos disponibles)"],
        index=0 if model_paths else 0,
        disabled=not bool(model_paths),
        help="Por defecto se usa el más reciente en nodeC/models/avg/.",
    )

    with st.form("patient_form"):
        st.markdown("### Variables binarias (0/1)")
        cols = st.columns(2)
        for i, (k, label) in enumerate(BIN_FEATURES):
            with cols[i % 2]:
                val = st.radio(
                    label,
                    options=[0, 1],
                    index=0 if st.session_state.form.get(k) in (None, 0) else 1,
                    horizontal=True,
                    help="0 = No, 1 = Sí (en Sex: 1 Hombre / 0 Mujer)",
                    key=f"form_{k}",
                )
                st.session_state.form[k] = int(val)

        st.markdown("### Variables numéricas")
        cols = st.columns(2)
        for i, (k, label, mn, mx) in enumerate(NUM_FEATURES):
            with cols[i % 2]:
                default = st.session_state.form.get(k)
                if default is None:
                    default = float(mn)
                val = st.number_input(
                    label,
                    min_value=float(mn),
                    max_value=float(mx),
                    value=float(default),
                    step=1.0,
                    help=f"Rango permitido: {mn}–{mx}",
                    key=f"form_{k}",
                )
                st.session_state.form[k] = float(val)

        st.markdown("### Variables categóricas / ordinales")
        cols = st.columns(2)
        for i, (k, label, mn, mx) in enumerate(ORD_FEATURES):
            with cols[i % 2]:
                default = st.session_state.form.get(k)
                if default is None:
                    default = int(mn)
                val = st.number_input(
                    label,
                    min_value=int(mn),
                    max_value=int(mx),
                    value=int(default),
                    step=1,
                    help=f"Rango permitido: {mn}–{mx}",
                    key=f"form_{k}",
                )
                st.session_state.form[k] = int(val)

        colA, colB = st.columns(2)
        with colA:
            submitted = st.form_submit_button("Evaluar", use_container_width=True)
        with colB:
            reset = st.form_submit_button("Limpiar", use_container_width=True)

    if reset:
        st.session_state.form = {k: None for k in FEATURE_ORDER}
        st.session_state.last_result = None
        st.session_state.last_report = ""
        st.rerun()

    if submitted:
        errors = validate_form(st.session_state.form)
        if errors:
            st.error("Corrige lo siguiente antes de evaluar:")
            for e in errors:
                st.write(f"- {e}")
        else:
            if not model_paths:
                st.error("No hay modelo .keras disponible para evaluar.")
            else:
                result = predict_risk_keras(st.session_state.form, selected_model)
                st.session_state.last_result = result
                st.session_state.last_report = ""

    # Mostrar el último resultado aunque haya reruns
    if st.session_state.last_result:
        result = st.session_state.last_result

        st.success("Evaluación generada (modelo real).")
        st.metric("Riesgo estimado", f"{result['level']}")
        st.write(f"Probabilidad: **{result['probability']:.4f}**")
        st.caption(result["disclaimer"])
        st.caption(f"Modelo usado: {result['model_path']}")

        # =========================
        # Impacto económico (simulador)
        # =========================
        st.markdown("## Impacto económico (simulación)")
        st.caption(
            "Estos cálculos son una *estimación por escenarios* basada en supuestos editables. "
            "No representan costos reales universales ni sustituyen análisis financieros institucionales."
        )
        
        with st.expander("Configurar supuestos económicos", expanded=True):
            col1, col2 = st.columns(2)
        
            with col1:
                costo_evento = st.number_input(
                    "Costo promedio por evento/complicación (USD)",
                    min_value=0.0,
                    value=1200.0,
                    step=50.0,
                    help="Ejemplo: costo promedio de una complicación, consulta tardía u hospitalización relacionada.",
                    key="eco_costo_evento",
                )
        
            with col2:
                reduccion_pct = st.slider(
                    "Reducción estimada por detección temprana (%)",
                    min_value=0,
                    max_value=100,
                    value=25,
                    step=1,
                    help="Cuánto se reduce el costo esperado si se detecta antes (por mejoras de manejo/prevención).",
                    key="eco_reduccion_pct",
                )
        
        st.divider()
        
        # Cálculo determinístico (Python): ahorro esperado por paciente
        prob = float(result["probability"])
        reduccion = float(reduccion_pct) / 100.0
        
        costo_esperado_sin = prob * float(costo_evento)
        ahorro_esperado = costo_esperado_sin * reduccion
        costo_esperado_con = max(0.0, costo_esperado_sin - ahorro_esperado)
        
        colA, colB, colC = st.columns(3)
        with colA:
            st.metric("Costo esperado sin intervención (USD)", f"{costo_esperado_sin:,.2f}")
        with colB:
            st.metric("Ahorro esperado (USD)", f"{ahorro_esperado:,.2f}")
        with colC:
            st.metric("Costo esperado con detección temprana (USD)", f"{costo_esperado_con:,.2f}")
        
        st.markdown(
            f"""
        *Interpretación*
        
        - Probabilidad estimada de riesgo: *{prob:.2%}*
        - Costo promedio asumido por evento: *${costo_evento:,.0f}*
        - Reducción asumida por detección temprana: *{reduccion_pct}%*
        
        *Ahorro esperado aproximado:* *${ahorro_esperado:,.2f} por paciente*
        
        Este valor es una estimación ilustrativa basada en supuestos ajustables.
        """
        )

        with st.expander("Generar informe narrativo (pitch) con Ollama", expanded=True):
            if st.button("Generar informe", use_container_width=True, key="btn_report"):
                with st.spinner("Generando informe con el LLM..."):
                    ctx = (
                        "Genera un informe profesional, sin diagnóstico médico.\n\n"
                        f"Inputs (features): {st.session_state.form}\n"
                        f"Salida del modelo: pred={result['pred_label']} prob={result['probability']:.4f} "
                        f"(nivel {result['level']}, umbral {result['threshold']})\n\n"
                        f"Estimación calculada (Python): costo_sin={costo_esperado_sin:.2f}, ahorro={ahorro_esperado:.2f}, costo_con={costo_esperado_con:.2f}\n\n"
                        f"Supuestos económicos: costo_evento_usd={costo_evento}, reduccion_pct={reduccion_pct}\n"
                        "Estructura requerida:\n"
                        "1) Resumen entendible del perfil\n"
                        "2) Interpretación del riesgo con disclaimer\n"
                        "3) Recomendaciones generales de prevención (no médicas)\n"
                        "4) Estimación económica del ahorro esperado por paciente y supuestos económicos\n"
                        "5) Cierre destacando privacidad y colaboración inter-hospitalaria (federated learning)\n"
                    )
                    st.session_state.chat_messages.append({"role": "user", "content": ctx})
                    reply = llm_reply(st.session_state.chat_messages, mode="free")
                    if not reply:
                        reply = "No recibí respuesta del modelo. Intenta nuevamente."
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    st.session_state.last_report = reply

            if st.session_state.last_report:
                st.markdown("#### Informe generado")
                st.write(st.session_state.last_report)

# -------------------------
# Chat
# -------------------------
with tab_chat:
    st.subheader("Chat de apoyo (explicaciones y dudas)")
    st.write("Úsalo para preguntar sobre variables, formatos, federated learning y la interpretación del resultado.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("Pregunta aquí (ej: ¿Qué significa NoDocbcCost?)")

    if user_q:
        st.session_state.chat_messages.append({"role": "user", "content": user_q})

        with st.chat_message("user"):
            st.write(user_q)

        thinking_placeholder = st.empty()
        with thinking_placeholder.container():
            with st.chat_message("assistant"):
                st.write("Pensando...")

        reply = llm_reply(st.session_state.chat_messages, mode="free")
        if not reply:
            reply = "No recibí respuesta del modelo. Intenta nuevamente."

        thinking_placeholder.empty()
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()