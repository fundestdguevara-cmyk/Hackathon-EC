
# 🤖 Asistente Legal con Telegram y Pinecone

Este proyecto implementa un **Chatbot legal** que permite consultar artículos de leyes ecuatorianas a través de **Telegram**, utilizando **FastAPI**, **Pinecone** y **Sentence Transformers** para búsqueda semántica.

---

## 🚀 Características

- 📚 Indexa automáticamente leyes en formato PDF (COIP, Código del Trabajo, LOEI, Transporte).
- 🔎 Búsqueda semántica con embeddings y re-rankeo con CrossEncoder.
- 🤖 Bot de Telegram con menú interactivo para seleccionar la ley.
- ⚡ API REST con FastAPI para responder consultas legales.
- 🗂 Manejo de artículos e incisos con regex robusto.
- 🔐 Variables de entorno para configuración segura.

---

## 📦 Instalación

### 1. Clonar repositorio
```bash
git clone https://github.com/tuusuario/asistente-legal.git
cd asistente-legal
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto con:

```env
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_INDEX_NAME=legal-assistant
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
```

---

## 📂 Estructura del proyecto

```
├── app/
│   ├── ingest.py          # Parser de PDFs → artículos
│   ├── index.py           # Conexión con Pinecone y embeddings
│   └── searcher.py        # LegalSearcher con CrossEncoder
├── api.py                 # FastAPI para consultas
├── telegram_bot.py        # Bot de Telegram
├── run_index.py           # Indexa todos los PDFs en Pinecone
├── reset_index.py         # Reinicia el índice en Pinecone
├── requirements.txt       # Dependencias
├── README.md              # Documentación
└── data/                  # Carpeta con PDFs de leyes
```

---

## ▶️ Uso

### 1. Indexar leyes

Coloca tus PDFs en la carpeta `data/` y ejecuta:

```bash
python run_index.py
```

### 2. Levantar API

```bash
uvicorn api:app --reload --port 8001
```

### 3. Iniciar bot de Telegram

```bash
python telegram_bot.py
```

---

### Nota
Para el correcto funcionamiento, es indipensable crear una cuenta en PINECONE, y colocar sus API KEY, en el archivo .env


## 📚 Ejemplo de consulta

En Telegram:

1. Selecciona la ley desde el menú.
2. Pregunta:

   ```
   "Pregunta segun la ley elegida"
   ```
3. El bot responde con el texto del artículo y cita.

---

## 🛠 Tecnologías

* [FastAPI](https://fastapi.tiangolo.com/)
* [Pinecone](https://www.pinecone.io/)
* [Sentence Transformers](https://www.sbert.net/)
* [Python Telegram Bot](https://python-telegram-bot.org/)
* [PyPDF2](https://pypi.org/project/PyPDF2/) / [pdfplumber](https://pypi.org/project/pdfplumber/)

---

## 👨‍💻 Autor

Proyecto desarrollado por **DeveloperChat** como asistente legal inteligente para consultas rápidas de normativa ecuatoriana.