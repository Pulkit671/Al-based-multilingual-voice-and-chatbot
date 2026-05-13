from __future__ import annotations

from app.rag.embed_store import get_embedding_model, get_or_create_collection


def retrieve_context(query: str, k: int = 5) -> list[str]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    collection = get_or_create_collection()
    if collection.count() == 0:
        return []

    embedding = get_embedding_model().encode([cleaned_query], convert_to_numpy=True).tolist()[0]
    result = collection.query(
        query_embeddings=[embedding],
        n_results=k,
    )

    documents = result.get('documents', [[]])[0]
    return [' '.join(str(document).split()) for document in documents if str(document).strip()]
