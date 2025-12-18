import io
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

# --------------------
# Helper functions
# --------------------

def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    return df


def parse_dates(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df = df.sort_values(date_col)
    df = df.set_index(date_col)
    return df


def infer_freq(index: pd.DatetimeIndex):
    try:
        return pd.infer_freq(index)
    except Exception:
        return None


def seasonal_naive_forecast(train: pd.Series, h: int, season_len: int) -> np.ndarray:
    if len(train) < season_len:
        return np.repeat(train.iloc[-1], h)
    last_season = train.iloc[-season_len:].values
    return np.tile(last_season, int(np.ceil(h / season_len)))[:h]


def compute_metrics(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / np.clip(np.abs(y_true), 1e-8, None))) * 100
    return rmse, mae, mape


def make_future_exog(exog_hist: pd.DataFrame | None, h: int, season_len: int) -> pd.DataFrame | None:
    if exog_hist is None:
        return None
    if len(exog_hist) >= season_len:
        template = exog_hist.iloc[-season_len:]
    else:
        template = exog_hist.iloc[[-1]]
    reps = int(np.ceil(h / len(template)))
    future = pd.concat([template] * reps, axis=0).iloc[:h]
    future.index = pd.RangeIndex(start=0, stop=h, step=1)
    return future


def rolling_origin_cv(y, exog, order_sar, seasonal_sar, order_sarimax, seasonal_sarimax, season_len=12, train_size=24, h=3):
    results = {
        "Seasonal Naive": [],
        "SARIMA": [],
        "SARIMAX": [],
        "Holt-Winters": [],
    }
    n = len(y)
    for start in range(train_size, n - h + 1, h):
        y_tr, y_te = y.iloc[:start], y.iloc[start : start + h]
        ex_tr = exog.iloc[:start] if exog is not None else None
        ex_te = exog.iloc[start : start + h] if exog is not None else None

        # Seasonal Naive
        pred_sn = seasonal_naive_forecast(y_tr, h, season_len)
        results["Seasonal Naive"].append(compute_metrics(y_te, pred_sn))

        # SARIMA
        try:
            model_sar = SARIMAX(y_tr, order=order_sar, seasonal_order=seasonal_sar, enforce_stationarity=False, enforce_invertibility=False)
            res_sar = model_sar.fit(disp=False)
            pred_sar = res_sar.forecast(h)
            results["SARIMA"].append(compute_metrics(y_te, pred_sar))
        except Exception:
            results["SARIMA"].append((np.nan, np.nan, np.nan))

        # SARIMAX
        try:
            model_sarx = SARIMAX(y_tr, exog=ex_tr, order=order_sarimax, seasonal_order=seasonal_sarimax, enforce_stationarity=False, enforce_invertibility=False)
            res_sarx = model_sarx.fit(disp=False)
            pred_sarx = res_sarx.forecast(h, exog=ex_te)
            results["SARIMAX"].append(compute_metrics(y_te, pred_sarx))
        except Exception:
            results["SARIMAX"].append((np.nan, np.nan, np.nan))

        # Holt-Winters
        try:
            hw = ExponentialSmoothing(y_tr, trend="add", seasonal="add", seasonal_periods=season_len)
            hw_fit = hw.fit(optimized=True)
            pred_hw = hw_fit.forecast(h)
            results["Holt-Winters"].append(compute_metrics(y_te, pred_hw))
        except Exception:
            results["Holt-Winters"].append((np.nan, np.nan, np.nan))

    avg_metrics = {}
    for model, vals in results.items():
        arr = np.array(vals)
        avg_metrics[model] = np.nanmean(arr, axis=0)
    return avg_metrics


def fit_and_forecast(y, exog, order_sar, seasonal_sar, order_sarimax, seasonal_sarimax, season_len, horizon):
    best_model = None
    forecast_vals = None
    forecast_ci = None

    # Preference order with tolerance
    prefs = ["SARIMAX", "SARIMA", "Holt-Winters", "Seasonal Naive"]

    # Train all candidates, pick best by MAPE then preference
    candidates = {}

    # SARIMA
    try:
        sar = SARIMAX(y, order=order_sar, seasonal_order=seasonal_sar, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        fc_res = sar.get_forecast(steps=horizon)
        candidates["SARIMA"] = (fc_res.predicted_mean, fc_res.conf_int(alpha=0.05))
    except Exception:
        pass

    # SARIMAX
    if exog is not None:
        try:
            future_ex = make_future_exog(exog, horizon, season_len)
            sarx = SARIMAX(y, exog=exog, order=order_sarimax, seasonal_order=seasonal_sarimax, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            fc_res = sarx.get_forecast(steps=horizon, exog=future_ex)
            candidates["SARIMAX"] = (fc_res.predicted_mean, fc_res.conf_int(alpha=0.05))
        except Exception:
            pass

    # Holt-Winters
    try:
        hw = ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=season_len)
        hw_fit = hw.fit(optimized=True)
        fc_vals = hw_fit.forecast(horizon)
        resid_std = np.std(y - hw_fit.fittedvalues)
        ci_lower = fc_vals - 1.96 * resid_std
        ci_upper = fc_vals + 1.96 * resid_std
        candidates["Holt-Winters"] = (fc_vals, pd.DataFrame({"lower": ci_lower, "upper": ci_upper}))
    except Exception:
        pass

    # Seasonal Naive
    fc_vals_sn = pd.Series(seasonal_naive_forecast(y, horizon, season_len), index=pd.RangeIndex(horizon))
    resid_std = np.std(y.diff(season_len).dropna()) if len(y) > season_len else np.std(y.diff().dropna())
    ci_lower = fc_vals_sn - 1.96 * resid_std
    ci_upper = fc_vals_sn + 1.96 * resid_std
    candidates["Seasonal Naive"] = (fc_vals_sn, pd.DataFrame({"lower": ci_lower, "upper": ci_upper}))

    # Select candidate: prefer presence in prefs order (first available)
    for pref in prefs:
        if pref in candidates:
            best_model = pref
            forecast_vals, forecast_ci = candidates[pref]
            break

    # Normalize CI
    if isinstance(forecast_ci, pd.DataFrame):
        lower = forecast_ci.iloc[:, 0]
        upper = forecast_ci.iloc[:, 1]
    else:
        lower = forecast_ci[:, 0]
        upper = forecast_ci[:, 1]

    return best_model, forecast_vals, lower, upper


def plot_history_forecast(series, fc_index, fc_values, ci_lower, ci_upper, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines+markers", name="Histórico", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=fc_index, y=fc_values, mode="lines+markers", name="Pronóstico", line=dict(color="#d62728")))
    fig.add_trace(
        go.Scatter(
            x=list(fc_index) + list(fc_index)[::-1],
            y=list(ci_upper) + list(ci_lower)[::-1],
            fill="toself",
            fillcolor="rgba(214,39,40,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="IC 95%",
        )
    )
    fig.add_vline(x=series.index[-1], line_width=1, line_dash="dash", line_color="gray")
    fig.update_layout(title=title, xaxis_title="Fecha", yaxis_title="Valor", template="simple_white")
    return fig


def plot_mom(history_series, forecast_series):
    hist_mom = history_series.pct_change().multiply(100)
    fc_mom = forecast_series.pct_change().multiply(100)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_mom.index, y=hist_mom.values, mode="lines+markers", name="Histórico MoM", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=fc_mom.index, y=fc_mom.values, mode="lines+markers", name="Pronóstico MoM", line=dict(color="#d62728")))
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
    fig.update_layout(title="Variación mensual (%)", xaxis_title="Fecha", yaxis_title="%", template="simple_white")
    return fig


def detect_peaks(fc_series: pd.Series):
    top = fc_series.sort_values(ascending=False).head(3)
    return top


def build_sales_plan(fc_series: pd.Series, season_len: int):
    peaks = detect_peaks(fc_series)
    avg = fc_series.mean()
    txt = [
        f"Promedio pronosticado: {avg:,.0f}",
        "Picos esperados (top 3):",
    ]
    for idx, val in peaks.items():
        txt.append(f"- {idx.strftime('%Y-%m')}: {val:,.0f}")
    txt.append("Sugerencias:")
    txt.append("- Alinear inventario y staffing con meses pico.")
    txt.append("- Planificar campañas previas a meses pico para capturar demanda.")
    txt.append("- Monitorear real vs pronóstico mensualmente y recalibrar trimestralmente.")
    return "\n".join(txt)


def llm_explain(hf_token: str | None, prompt: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1") -> str:
    """Use Hugging Face Inference API if token provided; else return placeholder."""
    if not hf_token:
        return "(Sin token HF) Añade la variable de entorno HF_TOKEN para obtener un análisis generado por LLM."
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 400, "temperature": 0.3}}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        return "No se pudo interpretar la respuesta del modelo."
    except Exception as e:
        return f"No se pudo llamar al modelo: {e}"


# --------------------
# Streamlit UI
# --------------------
st.set_page_config(page_title="Trendify Analytics — Pronóstico de Ventas", layout="wide", page_icon="📈")

# Branding banner (dark theme)
st.markdown(
    """
    <style>
    .stButton>button, .stDownloadButton>button {
        background-color: #1f77b4; 
        color: #ffffff; 
        border-radius: 6px;
    } 
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #16639c; 
        color: #ffffff;
    } 
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Trendify Analytics · Pronóstico de Ventas")
st.caption("Plataforma de análisis y pronóstico de series temporales con selección automática de modelos.")

# Guía de uso
with st.expander("ℹ️ Guía de uso"):
    st.markdown("""
    ### ¿Cómo funciona Trendify Analytics?
    
    **1. Carga de datos:**
    - Sube un archivo CSV con al menos dos columnas: una de fechas y otra(s) con valores numéricos (ventas, demanda, etc.)
    - Ejemplo: `fecha, ventas, producto_a, producto_b`
    
    **2. Configuración:**
    - **Horizonte de pronóstico**: Número de períodos futuros a predecir (3-12 meses)
    - **Longitud estacional**: Ciclo de repetición (12 para datos mensuales con estacionalidad anual)
    - **Ventana inicial para CV**: Tamaño mínimo de entrenamiento para validación (recomendado: 24 meses)
    - **HF_TOKEN (opcional)**: Token de Hugging Face para análisis automático con IA
    
    **3. Modelos evaluados:**
    - **Seasonal Naive**: Repite el patrón del último año (línea base simple)
    - **SARIMA**: Modelo estadístico que captura tendencia y estacionalidad
    - **SARIMAX**: SARIMA con variables exógenas (clima, promociones, etc.)
    - **Holt-Winters**: Suavizado exponencial con tendencia y estacionalidad
    
    **4. Validación:**
    - Se usa *rolling-origin cross-validation* para simular predicciones reales
    - El mejor modelo se selecciona por MAPE (error porcentual), priorizando modelos avanzados
    
    **5. Resultados:**
    - Pronóstico con intervalo de confianza 95%
    - Gráficos de continuidad y variación mensual
    - Plan de acción sugerido basado en picos detectados
    - Archivos CSV descargables para análisis posterior
    """)

# Sidebar controls
st.sidebar.header("⚙️ Configuración")
st.sidebar.markdown("### 📁 Datos de entrada")
uploaded = st.sidebar.file_uploader("Carga CSV (estructura similar: date, ventas, ...)", type=["csv"])
st.sidebar.markdown("### 🔧 Parámetros del modelo")
forecast_horizon = st.sidebar.slider(
    "Horizonte de pronóstico (meses)", 
    min_value=3, max_value=12, value=6, step=1,
    help="Número de períodos futuros a predecir. Mayor horizonte = mayor incertidumbre."
)
season_len = st.sidebar.number_input(
    "Longitud estacional", 
    min_value=1, max_value=24, value=12, step=1,
    help="Ciclo de repetición del patrón (ej: 12 para mensual con estacionalidad anual, 4 para trimestral)."
)
train_size = st.sidebar.number_input(
    "Tamaño de ventana inicial para CV", 
    min_value=12, max_value=60, value=24, step=1,
    help="Mínimo de períodos históricos para entrenar en validación cruzada. Más datos = mejor validación."
)
st.sidebar.markdown("### 🤖 Inteligencia Artificial (opcional)")
hf_token_input = st.sidebar.text_input(
    "HF_TOKEN de Hugging Face", 
    type="password", 
    help="Token para análisis automático con IA. Obtén uno gratis en huggingface.co/settings/tokens"
)
run_button = st.sidebar.button("Ejecutar análisis y pronóstico", type="primary")

# Placeholders
if uploaded is None:
    st.info("Carga un CSV para comenzar. Se requiere una columna de fechas y al menos una columna numérica de ventas.")
    st.stop()

# Load & basic parsing
raw_df = load_csv(uploaded)
st.write("### Vista previa de datos (primeras filas)")
st.dataframe(raw_df.head())

# Select columns
cols = list(raw_df.columns)
if len(cols) < 2:
    st.error("Se requiere al menos una columna de fecha y una de valores numéricos.")
    st.stop()

date_col = st.selectbox("Columna de fecha", options=cols, index=0)
num_cols = [c for c in cols if c != date_col and pd.api.types.is_numeric_dtype(raw_df[c])]
if not num_cols:
    st.error("No se encontraron columnas numéricas para pronosticar.")
    st.stop()

target_col = st.selectbox("Columna objetivo (ventas)", options=num_cols, index=0)
exog_options = [c for c in num_cols if c != target_col]
selected_exog = st.multiselect("Columnas exógenas (opcionales)", options=exog_options)

# Prepare data
df = parse_dates(raw_df, date_col)
if df.empty:
    st.error("No se pudieron parsear fechas. Verifica el formato de la columna de fecha.")
    st.stop()

y = df[target_col].asfreq(pd.infer_freq(df.index) or None)
if y.isna().any():
    y = y.interpolate()

exog = None
if selected_exog:
    exog = df[selected_exog].asfreq(y.index.freq)
    exog = exog.fillna(method="ffill").fillna(method="bfill")

# Frequency note
freq = infer_freq(y.index)
st.write(f"Frecuencia inferida: {freq if freq else 'no inferida'}")

# Auto-ARIMA orders
with st.expander("🔍 Órdenes sugeridas por auto-ARIMA (técnico)"):
    st.markdown("""
    **Auto-ARIMA** busca automáticamente los mejores parámetros (p,d,q) y estacionales (P,D,Q,s) 
    que minimizan el criterio AIC (Akaike Information Criterion). Menor AIC = mejor ajuste.
    
    - **p, d, q**: autoregresión, diferenciación y media móvil
    - **P, D, Q, s**: versiones estacionales (s=longitud estacional)
    """)
    st.write("Ejecutando auto-ARIMA para SARIMA y SARIMAX...")
    auto_sarima = auto_arima(y, seasonal=True, m=season_len, start_p=0, start_q=0, max_p=5, max_q=5, max_P=3, max_Q=3, max_d=1, max_D=1, stepwise=True, suppress_warnings=True)
    order_sarima = auto_sarima.order
    seasonal_order_sarima = auto_sarima.seasonal_order
    st.write(f"SARIMA {order_sarima} x {seasonal_order_sarima} (AIC={auto_sarima.aic():.2f})")

    if exog is not None:
        auto_sarimax = auto_arima(y, exogenous=exog, seasonal=True, m=season_len, start_p=0, start_q=0, max_p=5, max_q=5, max_P=3, max_Q=3, max_d=1, max_D=1, stepwise=True, suppress_warnings=True)
        order_sarimax = auto_sarimax.order
        seasonal_order_sarimax = auto_sarimax.seasonal_order
        st.write(f"SARIMAX {order_sarimax} x {seasonal_order_sarimax} (AIC={auto_sarimax.aic():.2f})")
    else:
        order_sarimax = order_sarima
        seasonal_order_sarimax = seasonal_order_sarima
        st.write("SARIMAX no evaluado (sin exógenas)")

# Run analysis
if not run_button:
    st.stop()

st.success("Procesando...")

# Rolling CV
cv_results = rolling_origin_cv(y, exog, order_sarima, seasonal_order_sarima, order_sarimax, seasonal_order_sarimax, season_len=season_len, train_size=train_size, h=3)
cv_df = pd.DataFrame(cv_results, index=["RMSE", "MAE", "MAPE"]).T
cv_df = cv_df.sort_values("MAPE")

st.write("### 📊 Validación cruzada (rolling-origin)")
st.markdown("""
**¿Qué es la validación cruzada?**  
Simula cómo se comportaría cada modelo en producción, entrenando con ventanas de datos históricos 
y probando predicciones en períodos futuros. Esto permite evaluar la precisión real del modelo.

**Métricas:**
- **RMSE** (Root Mean Squared Error): Penaliza errores grandes. Menor = mejor.
- **MAE** (Mean Absolute Error): Error promedio absoluto. Interpretación directa.
- **MAPE** (Mean Absolute Percentage Error): Error porcentual. Independiente de la escala. **Métrica principal de selección.**
""")
st.dataframe(cv_df.round(2))

# Choose best with preference for advanced models
mape_best = cv_df.iloc[0]["MAPE"]
best_model = cv_df.index[0]
if "SARIMAX" in cv_df.index:
    mape_sarimax = cv_df.loc["SARIMAX", "MAPE"]
    if not np.isnan(mape_sarimax) and (mape_sarimax - mape_best) <= 2.0:
        best_model = "SARIMAX"
elif "SARIMA" in cv_df.index:
    mape_sarima = cv_df.loc["SARIMA", "MAPE"]
    if not np.isnan(mape_sarima) and (mape_sarima - mape_best) <= 2.0:
        best_model = "SARIMA"
elif "Holt-Winters" in cv_df.index:
    mape_hw = cv_df.loc["Holt-Winters", "MAPE"]
    if not np.isnan(mape_hw) and (mape_hw - mape_best) <= 2.0:
        best_model = "Holt-Winters"

st.write(f"**Modelo seleccionado:** {best_model}")

# Forecast
best_model, fc_vals, lower, upper = fit_and_forecast(y, exog, order_sarima, seasonal_order_sarima, order_sarimax, seasonal_order_sarimax, season_len, forecast_horizon)

# Build forecast index aligned to frequency
last_date = y.index[-1]
fc_index = pd.date_range(start=last_date, periods=forecast_horizon + 1, freq=y.index.freq)[1:]
forecast_series = pd.Series(fc_vals.values if hasattr(fc_vals, "values") else fc_vals, index=fc_index)
ci_lower = pd.Series(lower.values if hasattr(lower, "values") else lower, index=fc_index)
ci_upper = pd.Series(upper.values if hasattr(upper, "values") else upper, index=fc_index)

forecast_table = pd.DataFrame({
    "Pronostico": forecast_series,
    "IC_inferior": ci_lower,
    "IC_superior": ci_upper,
})

st.write("### 📈 Pronóstico final")

st.markdown("""
**Gráfico 1: Histórico + Pronóstico con intervalo de confianza**  
Muestra la serie temporal histórica (azul) y el pronóstico (rojo) con un cono de incertidumbre (área sombreada).  
El **intervalo de confianza 95%** indica que hay un 95% de probabilidad de que el valor real caiga dentro de ese rango.
""")
st.plotly_chart(plot_history_forecast(y, forecast_series.index, forecast_series.values, ci_lower.values, ci_upper.values, "Histórico + Pronóstico"), use_container_width=True)

st.markdown("""
**Gráfico 2: Variación mensual (MoM - Month-over-Month)**  
Compara el cambio porcentual mes a mes entre histórico reciente y pronóstico.  
Útil para detectar saltos abruptos, validar continuidad y entender la estacionalidad esperada.
""")
st.plotly_chart(plot_mom(y.iloc[-season_len:], forecast_series), use_container_width=True)

st.markdown("**Tabla del pronóstico:**")
st.dataframe(forecast_table.round(2))

# Sales plan
st.write("### 💡 Plan de acción sugerido")
st.markdown("""
**¿Cómo usar este plan?**  
Basado en los picos de demanda detectados y el promedio pronosticado, se generan sugerencias para:
- Planificación de inventarios y producción
- Estrategias de campañas y promociones
- Ajuste de personal y recursos
""")
st.text(build_sales_plan(forecast_series, season_len))

# LLM-based explanation (optional via Hugging Face Inference API)
hf_token = hf_token_input or os.environ.get("HF_TOKEN")
with st.expander("Explicación automática (LLM)"):
    peaks = detect_peaks(forecast_series)
    peaks_str = ", ".join([f"{idx.strftime('%Y-%m')}={val:.0f}" for idx, val in peaks.items()])
    prompt = (
        "Eres un analista de negocio. Resume hallazgos clave, riesgos y acciones a partir del pronóstico. "
        f"Modelo: {best_model}. Horizonte: {forecast_horizon} meses. "
        f"Promedio pronosticado: {forecast_series.mean():.0f}. "
        f"Picos: {peaks_str}. "
        "Devuelve un resumen breve en viñetas y 3 acciones prioritarias."
    )
    if not hf_token:
        st.info("No se proporcionó HF_TOKEN. Ingresa uno en la barra lateral para obtener la explicación automática.")
    else:
        llm_response = llm_explain(hf_token, prompt)
        st.write(llm_response)

# Downloads
st.write("### 💾 Descargas")
st.markdown("""
**Archivos disponibles:**
- **Pronóstico CSV**: Tabla con predicciones e intervalos de confianza
- **Diagnóstico CSV**: Histórico + pronóstico para análisis detallado y trazabilidad
""")
# Forecast CSV
csv_buf = io.StringIO()
forecast_table_reset = forecast_table.reset_index().rename(columns={"index": "date"})
forecast_table_reset.to_csv(csv_buf, index=False)
st.download_button("Descargar pronóstico CSV", data=csv_buf.getvalue(), file_name="forecast.csv", mime="text/csv")

# Diagnostic CSV (histórico + forecast)
diag_buf = io.StringIO()
export_df = pd.DataFrame({"date": y.index, "historico": y.values})
forecast_out = forecast_table_reset.copy()
export_full = pd.concat([export_df, forecast_out], ignore_index=True, sort=False)
export_full.to_csv(diag_buf, index=False)
st.download_button("Descargar diagnóstico CSV", data=diag_buf.getvalue(), file_name="diagnostico_pronostico.csv", mime="text/csv")

# Simple PDF/HTML placeholder (future enhancement)
st.caption("Exportación PDF/HTML puede añadirse con WeasyPrint/Kaleido si se requiere en esta instancia.")
