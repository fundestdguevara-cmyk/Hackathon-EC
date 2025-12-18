import os
import re
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-assistant")

def init_pinecone():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

def build_embeddings_model():
    return SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

def build_text_for_embedding(article: Dict) -> str:
    title = article.get("title", "")
    body = article.get("body", "")
    return f"Artículo {article['article_number']}: {title}\n{body}"

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def upsert_articles(index, model, articles: List[Dict], source_name: str):
    to_upsert = []
    for a in articles:
        text = build_text_for_embedding(a)
        chunks = chunk_text(text, chunk_size=3000, overlap=300)
        for i, chunk in enumerate(chunks):
            vec = model.encode(chunk).tolist()
            metadata = {
                "article_number": a["article_number"],
                "title": a.get("title", ""),
                "text": chunk,
                "source": source_name,
            }
            vector_id = f"{a['id']}_chunk{i}"
            to_upsert.append((vector_id, vec, metadata))
    index.upsert(vectors=to_upsert)

def _normalize(s: str) -> str:
    s = (s or "").lower().strip()
    return (
        s.replace("á", "a")
         .replace("é", "e")
         .replace("í", "i")
         .replace("ó", "o")
         .replace("ú", "u")
    )

def query_index(question: str, top_k: int = 3, source: str = None) -> List[Dict]:
    index = init_pinecone()
    model = build_embeddings_model()

    query_vector = model.encode(question).tolist()
    response = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    results = [m["metadata"] for m in response.get("matches", [])]

    if source:
        norm_source = _normalize(source)
        results = [r for r in results if _normalize(r.get("source")) == norm_source]

    match = re.search(r"art[íi]culo\s*(\d+[A-Za-z\.]*)", question.lower())
    if match:
        articulo = match.group(1)
        exact_results = [r for r in results if r.get("article_number") == articulo]
        if exact_results:
            return exact_results

    ql = question.lower()
    results = sorted(results, key=lambda r: ql in (r.get("text", "").lower()), reverse=True)
    return results