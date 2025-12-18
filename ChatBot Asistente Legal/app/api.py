from fastapi import FastAPI, Request
from app.index import query_index
import re

app = FastAPI()

@app.post("/ask/{ley}")
async def ask_ley(ley: str, request: Request):
    body = await request.json()
    question = body.get("question", "")
    top_k = int(body.get("top_k", 3))

    results = query_index(question, top_k=top_k, source=ley)

    if not results:
        return {
            "respuesta": [{
                "artículo": "—",
                "título": "Sin coincidencias",
                "extracto": "No se encontró información relevante. Intenta mencionar número de artículo o palabras clave."
            }]
        }

    # 🔹 Si hay coincidencia exacta por artículo, mostrar solo ese
    match = re.search(r"art[íi]culo\s*(\d+)", question.lower())
    if match:
        articulo = match.group(1)
        exact = [r for r in results if r.get("article_number") == articulo]
        if exact:
            r = exact[0]
            return {
                "respuesta": [{
                    "artículo": r.get("article_number"),
                    "título": r.get("title"),
                    "extracto": (r.get("text") or "")[:800] + "..."
                }]
            }

    # 🔹 Si no hay coincidencia exacta, mostrar los 3 más relevantes
    formatted = []
    for r in results[:3]:
        formatted.append({
            "artículo": r.get("article_number"),
            "título": r.get("title"),
            "extracto": (r.get("text") or "")[:800] + "..."
        })

    return {"respuesta": formatted}