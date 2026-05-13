from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.rag.pdf_ingest import extract_pdf_chunks

settings = get_settings()


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.sentence_transformer_model_name)


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    vector_dir = Path(settings.vector_db_dir)
    vector_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(vector_dir))


def get_or_create_collection() -> Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(name=settings.chroma_collection_name)


def build_vector_store(reset: bool = False) -> int:
    documents = extract_pdf_chunks()
    collection = get_or_create_collection()

    if reset:
        client = get_chroma_client()
        client.delete_collection(settings.chroma_collection_name)
        collection = client.get_or_create_collection(name=settings.chroma_collection_name)

    if not documents:
        return 0

    texts = [item['text'] for item in documents]
    ids = [item['id'] for item in documents]
    metadatas = [item['metadata'] for item in documents]
    embeddings = get_embedding_model().encode(texts, convert_to_numpy=True).tolist()

    existing_ids = set(collection.get(include=[])['ids'])
    new_records = [
        (doc_id, text, metadata, embedding)
        for doc_id, text, metadata, embedding in zip(ids, texts, metadatas, embeddings)
        if doc_id not in existing_ids
    ]
    if not new_records:
        return 0

    collection.add(
        ids=[record[0] for record in new_records],
        documents=[record[1] for record in new_records],
        metadatas=[record[2] for record in new_records],
        embeddings=[record[3] for record in new_records],
    )
    return len(new_records)


if __name__ == '__main__':
    added = build_vector_store(reset=True)
    print(f'Added {added} chunks to Chroma DB at {settings.vector_db_dir}')
