from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'MedAI Chatbot'
    app_version: str = '0.1.0'
    secret_key: str = 'change-me'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24
    mongodb_uri: str = 'mongodb://localhost:27017'
    mongodb_db_name: str = 'med_ai_chatbot'
    cors_origins: list[str] = ['http://localhost:5173']
    cors_origin_regex: str = r'https?://(localhost|127\.0\.0\.1)(:\d+)?$'
    upload_dir: str = str(Path(__file__).resolve().parent / 'uploads' / 'voice')
    default_language: str = 'en'
    app_dir: str = str(Path(__file__).resolve().parent)
    biobert_base_model_name: str = 'dmis-lab/biobert-base-cased-v1.1'
    biobert_model_dir: str = str(Path(__file__).resolve().parent / 'models' / 'biobert_model')
    sentence_transformer_model_name: str = 'all-MiniLM-L6-v2'
    cohere_api_key: str | None = None
    cohere_model_name: str = 'command-a-03-2025'
    vector_db_dir: str = str(Path(__file__).resolve().parent / 'vector_db')
    chroma_collection_name: str = 'medical_knowledge'
    data_dir: str = str(Path(__file__).resolve().parent / 'data')
    pdf_data_dir: str = str(Path(__file__).resolve().parent / 'data' / 'pdfs')
    symptoms_dataset_csv: str = str(Path(__file__).resolve().parent / 'data' / 'symptoms_disease.csv')
    disease_info_csv: str = str(Path(__file__).resolve().parent / 'data' / 'disease_info.csv')
    biobert_label_map_file: str = str(Path(__file__).resolve().parent / 'models' / 'biobert_model' / 'label_mapping.json')
    rag_chunk_size_words: int = 420
    rag_chunk_overlap_words: int = 80

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
