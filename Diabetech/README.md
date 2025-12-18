# DiabeTech — Federated Learning + Assistant for Diabetes Risk Prediction

## Overview

**DiabeTech** is an end‑to‑end demo system for **diabetes risk prediction** using **Federated Learning (FL)** with a **Multilayer Perceptron (MLP)** and **real TCP socket communication** orchestrated with **Docker Compose**. It also includes a **Streamlit application** that:

- Collects clinical inputs via a validated form (matching the dataset schema),
- Runs **real inference** using the latest aggregated **`.keras` global model**,
- Provides an **AI assistant** powered by **Ollama + RAG (Chroma)** to explain variables, input formats, federated learning, and result interpretation,
- Includes an **assumption‑based economic impact** panel (transparent and configurable).

Core idea: **multiple hospitals can collaboratively train a useful predictive model without sharing raw patient data**.

---

## Key Features

- Centralized Federated Learning (fixed server aggregator)
- Semi‑decentralized FL option supported in the FL core (leader rotation logic via `coordination.py`)
- Real TCP sockets between nodes (server/client modules)
- Multi‑node deployment via Docker Compose
- Global aggregated models exported as **TensorFlow `.keras`**
- Streamlit UI for:
  - Clinical form + validation
  - Real inference from global models
  - Economic impact sliders (assumption‑based, with disclaimer)
  - Chat assistant (Ollama) + RAG with Chroma vector stores

---

## How It Works

### Federated Learning Flow (high level)

1. Each node (hospital) loads its **local data partition** from `server/diabetes_divided/diabetes_<id>.csv`.
2. Nodes train locally and exchange **model parameters only** (never raw patient data).
3. The server aggregates updates using **FedAvg** and saves global models into:
   - `server/nodeC/models/avg/`

### Streamlit App Flow

1. User fills the clinical form (21 features).
2. App loads the most recent (or selected) `.keras` model from the global model directory.
3. App produces a probability + risk band (Bajo / Moderado / Elevado).
4. The assistant (Ollama + RAG) can explain:
   - What each feature means,
   - Which values are valid,
   - What the prediction implies in demo terms (with medical disclaimer).

---

## Project Structure (real repository layout)

This is the **actual structure** as implemented:

```text
DIABETECH/
│
├── app.py                   # Streamlit app: form + real inference + chatbot + economic sliders
├── llm.py                   # Ollama LLM + Multi-DB Chroma RAG logic (explanations grounded in docs)
├── README.md                # This file
├── requirements.txt         # Python dependencies (Streamlit + TF + Ollama + Chroma + LangChain)
│
├── rag/                     # RAG source docs + vectorization script
│   ├── GuiaPacientesDiabetes.pdf
│   ├── spanish-tasty-recipe-508.pdf
│   └── rag_creation.py      # Builds Chroma vector DBs from PDFs (collections)
│
├── vectors/                 # Chroma vector stores (persisted)
│   ├── first/               # Example collection 1 (chroma.sqlite3 + embeddings)
│   └── second/              # Example collection 2 (chroma.sqlite3 + embeddings)
│
└── server/                  # Federated Learning core (Dockerized multi-node runtime)
    ├── diabetes_divided/    # Data partitions per node
    │   ├── diabetes_1.csv
    │   ├── diabetes_2.csv
    │   ├── diabetes_3.csv
    │   └── diabetes_4.csv
    │
    ├── nodeC/               # Aggregation/server logic (FedAvg + model persistence)
    │   ├── avg_model.py
    │   ├── connections.py
    │   └── server.py
    │
    ├── nodex/               # Client logic (local training + send/receive weights)
    │   ├── client.py
    │   ├── connections.py
    │   └── model_build.py
    │
    ├── coordination.py      # Leader selection logic (used for semi-decentralized mode)
    ├── main.py              # Entry point for FL rounds/sub-rounds
    ├── metrics.sh           # HW metrics collection for leader selection
    ├── utils.py             # Helpers: convergence, CSV merge, etc.
    ├── Dockerfile
    ├── docker-compose.yaml
    └── requirements.txt     # FL runtime deps (server side)
```

---

## Requirements

### 1) Local (Streamlit + RAG + Inference)

- Python 3.10+ recommended
- Ollama installed and running
- Models available in Ollama:
  - **Chat model** (example): `qwen2.5:3b`
  - **Embedding model** (example): `nomic-embed-text:latest`

Install Python deps:

```bash
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app.py
```

### 2) Federated Learning Runtime (Docker)

Docker + Docker Compose required.

---

## Running Federated Learning (Docker)

From the **`server/`** directory:

### Build image

```bash
docker build -t federated-semidescentralized_image .
```

### Start the multi-node FL system

```bash
docker compose up
```

Artifacts produced:

- Global models: `server/nodeC/models/avg/*.keras`
- Per-node logs (if mounted): `server/nodo*/nodo*.log` (depending on your compose volumes)
- Metrics CSVs: `server/full_metrics_node_#.csv` (if enabled in your workflow)

---

## Building / Refreshing the RAG Vector Stores

DiabeTech uses persisted Chroma stores in `vectors/`.

If you update PDFs or want to rebuild embeddings, run:

```bash
python rag/rag_creation.py
```

Make sure Ollama is running and the embedding model exists (e.g., `nomic-embed-text:latest`).

---

## Dataset and Feature Schema (21 inputs)

The model expects **21 input features** (numeric: binary/ordinal/continuous). The Streamlit form is aligned to this schema:

Binary (0=No, 1=Sí):

- HighBP, HighChol, CholCheck, Smoker, Stroke, HeartDiseaseorAttack, PhysActivity,
  Fruits, Veggies, HvyAlcoholConsump, AnyHealthcare, NoDocbcCost, DiffWalk, Sex

Continuous / integer:

- BMI (10–70), MentHlth (0–30), PhysHlth (0–30)

Ordinal:

- GenHlth (1–5), Age (1–14), Education (1–6), Income (1–8)

Note: the label column in the raw dataset is typically `Diabetes_binary` and is **not** part of the 21 inputs.

---

## Economic Impact Panel (Assumption‑Based)

The Streamlit app includes an **economic impact** section driven by **user‑controlled sliders** (e.g., cost per adverse event and expected reduction from early detection).

Important:

- This is **not** a medical or actuarial estimate.
- It is a **transparent scenario model** for hackathon demo purposes.
- The app displays an explicit disclaimer and keeps assumptions visible.

---

## Privacy & Safety Notes

- Raw patient data is never centralized in FL.
- Only model weights/parameters are shared.
- Outputs are for demonstration and educational use only.

**DiabeTech is not a diagnostic tool.**

---

DiabeTech shows how hospitals can **collaborate on AI models**, protect sensitive data via **Federated Learning**, and still deliver **actionable, explainable insights**—supported by a **RAG assistant** that improves usability for non‑technical stakeholders.
