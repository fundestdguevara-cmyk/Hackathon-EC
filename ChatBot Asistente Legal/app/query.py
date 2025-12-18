from typing import Dict, List
from sentence_transformers import SentenceTransformer, CrossEncoder

class LegalSearcher:
    def __init__(self, index, model: SentenceTransformer):
        self.index = index
        self.model = model
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    def search(self, user_query: str, top_k: int = 5) -> List[Dict]:
        qvec = self.model.encode(user_query).tolist()
        res = self.index.query(
            vector=qvec,
            top_k=max(top_k * 5, 20),
            include_metadata=True
        )

        candidates = []
        for m in res.matches or []:
            meta = m.metadata or {}
            candidates.append({
                "id": m.id,
                "score": m.score,
                "article_number": meta.get("article_number"),
                "title": meta.get("title"),
                "text": meta.get("text"),
                "source": meta.get("source"),
            })

        if not candidates:
            return []

        pairs = [(user_query, c.get("text", "")) for c in candidates]
        re_scores = self.reranker.predict(pairs)

        for c, s in zip(candidates, re_scores):
            c["re_rank_score"] = float(s)

        candidates.sort(key=lambda x: x["re_rank_score"], reverse=True)
        return candidates[:top_k]

def compose_answer(results: List[Dict], user_query: str) -> Dict:
    if not results:
        return {"respuesta": [{
            "artículo": "—",
            "título": "Sin coincidencias",
            "extracto": "No se encontró información relevante."
        }]}

    best = results[0]
    snippet = best.get("text", "No se encontró texto en la base de datos.")
    if snippet and len(snippet) > 1200:
        snippet = snippet[:1200] + "..."

    return {"respuesta": [{
        "artículo": best.get("article_number", "N/A"),
        "título": best.get("title", ""),
        "extracto": snippet,
        "fuente": best.get("source", "Desconocido"),
        "consulta": user_query
    }]}