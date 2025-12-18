import os
from dotenv import load_dotenv
from app.ingest import load_legal_articles
from app.index import build_embeddings_model, upsert_articles, init_pinecone

load_dotenv()

index = init_pinecone()
model = build_embeddings_model()

DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    print(f"⚠️ Carpeta {DATA_DIR} no encontrada.")
    exit(1)

pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]

if not pdf_files:
    print("⚠️ No se encontraron archivos PDF en la carpeta data.")
    exit(1)

for filename in pdf_files:
    path = os.path.join(DATA_DIR, filename)
    nombre_ley = os.path.splitext(filename)[0]
    articles = load_legal_articles(path)

    if not articles:
        print(f"⚠️ {nombre_ley}: no se detectaron artículos.")
        continue

    print(f"📄 {nombre_ley}: {len(articles)} artículos detectados")
    upsert_articles(index, model, articles, nombre_ley)
    print(f"✅ {len(articles)} artículos de {nombre_ley} insertados en Pinecone.")

print("🎉 Todas las leyes fueron indexadas en Pinecone.")