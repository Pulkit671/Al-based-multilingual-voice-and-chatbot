from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.config import get_settings

settings = get_settings()


def _normalize_disease_name(value: str) -> str:
    return ' '.join(str(value).strip().lower().split())


@lru_cache(maxsize=1)
def _load_disease_info() -> dict[str, dict[str, object]]:
    csv_path = Path(settings.disease_info_csv)
    if not csv_path.exists():
        return {}

    dataframe = pd.read_csv(csv_path).fillna('')
    info_map: dict[str, dict[str, object]] = {}
    for _, row in dataframe.iterrows():
        disease = str(row.get('disease', '')).strip()
        if not disease:
            continue

        precautions_raw = str(row.get('precautions', '')).strip()
        normalized_precautions = [
            item.strip(' -')
            for item in precautions_raw.replace('|', '\n').replace(';', '\n').splitlines()
            if item.strip(' -')
        ]

        info_map[_normalize_disease_name(disease)] = {
            'disease': disease,
            'description': str(row.get('description', '')).strip(),
            'precautions': normalized_precautions,
        }

    return info_map


def get_disease_info(disease: str) -> tuple[str | None, list[str]]:
    if not disease:
        return None, []

    info = _load_disease_info().get(_normalize_disease_name(disease))
    if not info:
        return None, []

    return info.get('description') or None, list(info.get('precautions', []))
