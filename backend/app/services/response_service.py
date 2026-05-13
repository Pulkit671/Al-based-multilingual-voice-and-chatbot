from __future__ import annotations

import re

from app.ml.biobert_predictor import UNKNOWN_DISEASE

DISCLAIMER = (
    'Consult a doctor if symptoms persist or worsen. This is informational guidance, not a final diagnosis.'
)

IMPORTANT_RAG_WORDS = (
    'symptom',
    'symptoms',
    'treatment',
    'treat',
    'cause',
    'causes',
    'fever',
    'pain',
    'infection',
    'prevent',
    'prevention',
    'risk',
    'diagnosis',
    'care',
)


def _shorten_text(text: str | None, limit: int = 120) -> str:
    if not text:
        return 'Basic disease information is not available in the knowledge file.'

    cleaned = ' '.join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned

    short_text = cleaned[:limit].rsplit(' ', 1)[0].rstrip('.,;:')
    return f'{short_text}.'


def _normalize_precautions(precautions: list[str] | str | None) -> list[str]:
    if not precautions:
        return []
    if isinstance(precautions, str):
        return [item.strip() for item in precautions.split(',') if item.strip()]
    return [str(item).strip() for item in precautions if str(item).strip()]


def _format_precautions(precautions: list[str] | str | None) -> str:
    precaution_items = _normalize_precautions(precautions)[:3]
    if not precaution_items:
        precaution_items = [
            'Drink enough fluids',
            'Take proper rest',
            'Consult a doctor if symptoms worsen',
        ]
    return '\n'.join(f'- {item}' for item in precaution_items)


def _extract_chunk_text(chunk: str | dict[str, object]) -> str:
    if isinstance(chunk, dict):
        return str(chunk.get('text', '')).strip()
    return str(chunk).strip()


def _sanitize_rag_text(text: str) -> str:
    cleaned = re.sub(r'\[[^\]]*(?:book|source|page|file|chapter)[^\]]*\]', ' ', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(?:book|source|file|chapter)\s*[:#-]?\s*[^\.;,\n]{0,80}', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bpage\s*(?:no\.?|number|#)?\s*\d+\b', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def filter_context(chunks: list[str] | list[dict[str, object]]) -> list[str]:
    important_lines: list[str] = []
    seen_lines = set()
    clean_chunks = [_sanitize_rag_text(_extract_chunk_text(chunk)) for chunk in chunks]
    clean_chunks = [chunk for chunk in clean_chunks if chunk]

    print('RAG chunks:', clean_chunks)

    for chunk in clean_chunks:
        normalized_chunk = chunk.replace('\n', ' ')
        sentences = [sentence.strip(' -:\t') for sentence in re.split(r'(?<=[.!?])\s+', normalized_chunk) if sentence.strip()]

        for sentence in sentences:
            lowered_sentence = sentence.lower()
            if not any(word in lowered_sentence for word in IMPORTANT_RAG_WORDS):
                continue

            clean_sentence = _shorten_text(sentence, 140)
            dedupe_key = clean_sentence.lower()
            if dedupe_key in seen_lines:
                continue

            seen_lines.add(dedupe_key)
            important_lines.append(clean_sentence)
            if len(important_lines) == 3:
                print('Filtered points:', important_lines)
                return important_lines

    print('Filtered points:', important_lines)
    return important_lines


def _format_rag_points(rag_chunks: list[str] | list[dict[str, object]]) -> str:
    rag_points = filter_context(rag_chunks)
    if not rag_points:
        return '- No extra PDF insight was found for these symptoms.'
    return '\n'.join(f'- {point}' for point in rag_points)


def generate_medical_response(
    user_symptoms: str,
    predicted_disease: str,
    description: str | None,
    precautions: list[str],
    rag_chunks: list[str] | list[dict[str, object]],
    confidence: float | None = None,
) -> str:
    disease = predicted_disease or UNKNOWN_DISEASE
    short_description = _shorten_text(description, 120)

    if disease == UNKNOWN_DISEASE:
        short_description = 'The symptoms do not confidently match one disease in the current model.'

    return (
        f'Predicted Disease:\n{disease}\n\n'
        f'Description:\n{short_description}\n\n'
        f'Precautions:\n{_format_precautions(precautions)}\n\n'
        f'Additional Insight:\n{_format_rag_points(rag_chunks)}\n\n'
        f'Note:\n{DISCLAIMER}'
    )
