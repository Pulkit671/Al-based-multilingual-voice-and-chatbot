from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import torch
from transformers import BertForSequenceClassification, BertTokenizer

from app.config import get_settings

settings = get_settings()

UNKNOWN_DISEASE = 'Unknown Condition'


@lru_cache(maxsize=1)
def _load_label_mapping() -> dict[int, str]:
    mapping_path = Path(settings.biobert_label_map_file)
    if not mapping_path.exists():
        raise FileNotFoundError(
            f'Label mapping not found at {mapping_path}. Train the BioBERT model first.'
        )
    raw_mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
    return {int(key): value for key, value in raw_mapping.items()}


@lru_cache(maxsize=1)
def _load_predictor_components():
    model_dir = Path(settings.biobert_model_dir)
    if not model_dir.exists():
        raise FileNotFoundError(
            f'BioBERT model directory not found at {model_dir}. Run train_biobert.py first.'
        )

    tokenizer = BertTokenizer.from_pretrained(str(model_dir))
    model = BertForSequenceClassification.from_pretrained(str(model_dir))
    model.eval()
    return tokenizer, model


def predict_disease_with_confidence(text: str) -> tuple[str, float]:
    cleaned_text = text.strip()
    if not cleaned_text:
        return UNKNOWN_DISEASE, 0.0

    try:
        tokenizer, model = _load_predictor_components()
        label_mapping = _load_label_mapping()
    except Exception:
        return UNKNOWN_DISEASE, 0.0

    encoded = tokenizer(
        cleaned_text,
        truncation=True,
        max_length=256,
        padding=True,
        return_tensors='pt',
    )

    with torch.no_grad():
        outputs = model(**encoded)
        probabilities = torch.softmax(outputs.logits, dim=-1)[0]

    prediction_index = int(torch.argmax(probabilities).item())
    confidence = float(probabilities[prediction_index].item())
    disease = label_mapping.get(prediction_index, UNKNOWN_DISEASE)
    if confidence < 0.35:
        return UNKNOWN_DISEASE, confidence
    return disease, confidence


def predict_disease(text: str) -> str:
    predicted_disease, _ = predict_disease_with_confidence(text)
    return predicted_disease
