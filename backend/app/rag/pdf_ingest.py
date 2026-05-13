from __future__ import annotations

from pathlib import Path

import fitz

from app.config import get_settings

settings = get_settings()


def _chunk_words(words: list[str], chunk_size: int, overlap: int) -> list[str]:
    if not words:
        return []

    chunks: list[str] = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk = ' '.join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
    return chunks


def extract_pdf_chunks(
    pdf_dir: str | Path | None = None,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[dict[str, object]]:
    source_dir = Path(pdf_dir or settings.pdf_data_dir)
    source_dir.mkdir(parents=True, exist_ok=True)

    resolved_chunk_size = chunk_size or settings.rag_chunk_size_words
    resolved_overlap = overlap or settings.rag_chunk_overlap_words
    documents: list[dict[str, object]] = []

    for pdf_path in sorted(source_dir.glob('*.pdf')):
        with fitz.open(pdf_path) as pdf_document:
            for page_index, page in enumerate(pdf_document):
                page_text = page.get_text('text').strip()
                if not page_text:
                    continue

                words = page_text.split()
                for chunk_index, chunk in enumerate(
                    _chunk_words(words, resolved_chunk_size, resolved_overlap)
                ):
                    documents.append(
                        {
                            'id': f'{pdf_path.stem}-p{page_index + 1}-c{chunk_index + 1}',
                            'text': chunk,
                            'metadata': {
                                'source_file': pdf_path.name,
                                'page_number': page_index + 1,
                                'chunk_index': chunk_index + 1,
                            },
                        }
                    )

    return documents


if __name__ == '__main__':
    chunks = extract_pdf_chunks()
    print(f'Extracted {len(chunks)} chunks from {settings.pdf_data_dir}')
