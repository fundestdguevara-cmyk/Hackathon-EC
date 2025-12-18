import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-assistant")

def reset_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # 🔹 Si el índice existe, borrarlo
    if INDEX_NAME in pc.list_indexes().names():
        pc.delete_index(INDEX_NAME)
        print(f"🗑️ Índice '{INDEX_NAME}' eliminado.")

    # 🔹 Crear índice nuevo
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,   # asegúrate que coincide con tu modelo
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print(f"✅ Índice '{INDEX_NAME}' recreado en Pinecone.")

if __name__ == "__main__":
    reset_index()