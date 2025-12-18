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
        for m in res.matches:
            meta = m.metadata or {}
            candidates.append({
                "id": m.id,
                "score": m.score,
                "article_number": meta.get("article_number"),
                "title": meta.get("title"),
                "text": meta.get("text"),
                "source": meta.get("source"),
            })

        pairs = [(user_query, c.get("text", "")) for c in candidates]
        re_scores = self.reranker.predict(pairs)

        for c, s in zip(candidates, re_scores):
            c["re_rank_score"] = float(s)

        candidates.sort(key=lambda x: x["re_rank_score"], reverse=True)
        return candidates[:top_k]

def compose_answer(results: List[Dict], user_query: str) -> str:
    if not results:
        return "No se encontró información relevante para tu consulta."
    best = results[0]
    citation = f"Artículo {best.get('article_number', 'N/A')} — {best.get('source', 'Desconocido')}"
    snippet = best.get("text", "No se encontró texto en la base de datos.")
    if snippet and len(snippet) > 1200:
        snippet = snippet[:1200] + "..."
    return (
        f"Según la normativa aplicable:\n\n"
        f"{snippet}\n\n"
        f"Cita: {citation}\n"
        f"(Consulta: \"{user_query}\")"
    )