from app.index import init_pinecone, build_embeddings_model

def list_articles_by_source(source_name: str, top_k: int = 200):
    index = init_pinecone()
    model = build_embeddings_model()

    # Consulta genérica para traer muchos artículos
    query_vector = model.encode("artículo").tolist()
    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    articles = [
        m["metadata"]["article_number"]
        for m in response.get("matches", [])
        if m["metadata"].get("source") == source_name
    ]

    print(f"📑 Artículos detectados en {source_name}:")
    print(sorted(set(articles)))

if __name__ == "__main__":
    list_articles_by_source("Código Orgánico Integral Penal")