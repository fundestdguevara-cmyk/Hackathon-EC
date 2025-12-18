import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from app.index import init_pinecone, build_embeddings_model
from app.query import LegalSearcher, compose_answer

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-assistant")

index = init_pinecone()
embed_model = build_embeddings_model()
searcher = LegalSearcher(index, embed_model)

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3

@app.post("/ask/{ley}")
async def ask_question(ley: str, request: QuestionRequest):
    try:
        results = searcher.search(request.question, top_k=request.top_k)
        results = [r for r in results if r.get("source") == ley]
        answer = compose_answer(results, request.question)
    except Exception as e:
        answer = f"⚠️ Error interno: {str(e)}"
    return {"answer": answer}

@app.get("/")
async def root():
    return {"status": "API Legal Assistant activa 🚀"}