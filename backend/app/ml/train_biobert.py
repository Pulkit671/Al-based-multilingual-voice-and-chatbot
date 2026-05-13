from __future__ import annotations

import json
import inspect
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import (
    BertConfig,
    BertForSequenceClassification,
    BertTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from app.config import get_settings

settings = get_settings()


@dataclass
class TrainingConfig:
    test_size: float = 0.2
    random_state: int = 42
    epochs: int = 3
    train_batch_size: int = 8
    eval_batch_size: int = 8
    learning_rate: float = 2e-5
    max_length: int = 256


class SymptomDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer, max_length: int) -> None:
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        encoded = self.tokenizer(
            self.texts[index],
            truncation=True,
            max_length=self.max_length,
            padding=False,
        )
        encoded['labels'] = self.labels[index]
        return {key: torch.tensor(value) for key, value in encoded.items()}


def _load_training_dataframe() -> pd.DataFrame:
    csv_path = Path(settings.symptoms_dataset_csv)
    if not csv_path.exists():
        raise FileNotFoundError(
            f'Symptoms dataset not found at {csv_path}. Expected columns: text, disease.'
        )

    dataframe = pd.read_csv(csv_path)
    required_columns = {'text', 'disease'}
    missing = required_columns.difference(dataframe.columns)
    if missing:
        raise ValueError(f'Missing required columns in symptoms dataset: {sorted(missing)}')

    cleaned = dataframe[['text', 'disease']].dropna()
    cleaned['text'] = cleaned['text'].astype(str).str.strip()
    cleaned['disease'] = cleaned['disease'].astype(str).str.strip()
    cleaned = cleaned[(cleaned['text'] != '') & (cleaned['disease'] != '')]
    if cleaned.empty:
        raise ValueError('Symptoms dataset is empty after cleaning.')
    return cleaned


def _encode_labels(labels: list[str]) -> tuple[list[int], list[str]]:
    classes = sorted(set(labels))
    label_to_id = {label: index for index, label in enumerate(classes)}
    return [label_to_id[label] for label in labels], classes


def _split_dataframe(dataframe: pd.DataFrame, test_size: float, random_state: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    shuffled = dataframe.sample(frac=1, random_state=random_state).reset_index(drop=True)
    eval_size = max(1, int(len(shuffled) * test_size))
    if eval_size >= len(shuffled):
        eval_size = 1
    eval_df = shuffled.iloc[:eval_size].reset_index(drop=True)
    train_df = shuffled.iloc[eval_size:].reset_index(drop=True)
    if train_df.empty:
        train_df = eval_df.copy()
    return train_df, eval_df


def _build_training_arguments(output_dir: Path, config: TrainingConfig) -> TrainingArguments:
    requested_args = {
        'output_dir': str(output_dir),
        'num_train_epochs': config.epochs,
        'per_device_train_batch_size': config.train_batch_size,
        'per_device_eval_batch_size': config.eval_batch_size,
        'learning_rate': config.learning_rate,
        'eval_strategy': 'epoch',
        'evaluation_strategy': 'epoch',
        'save_strategy': 'epoch',
        'report_to': 'none',
        'use_cpu': True,
        'no_cuda': True,
    }
    supported_args = inspect.signature(TrainingArguments.__init__).parameters
    filtered_args = {
        key: value
        for key, value in requested_args.items()
        if key in supported_args
    }
    return TrainingArguments(**filtered_args)


def _build_trainer(model, training_args, train_dataset, eval_dataset, tokenizer) -> Trainer:
    requested_args = {
        'model': model,
        'args': training_args,
        'train_dataset': train_dataset,
        'eval_dataset': eval_dataset,
        'tokenizer': tokenizer,
        'processing_class': tokenizer,
        'data_collator': DataCollatorWithPadding(tokenizer=tokenizer),
    }
    supported_args = inspect.signature(Trainer.__init__).parameters
    filtered_args = {
        key: value
        for key, value in requested_args.items()
        if key in supported_args
    }
    return Trainer(**filtered_args)


def train() -> None:
    config = TrainingConfig()
    dataframe = _load_training_dataframe()

    dataframe['label'], label_classes = _encode_labels(dataframe['disease'].tolist())
    train_df, eval_df = _split_dataframe(dataframe, config.test_size, config.random_state)

    tokenizer = BertTokenizer.from_pretrained(
        settings.biobert_base_model_name,
    )
    model_config = BertConfig.from_pretrained(settings.biobert_base_model_name)
    model_config.num_labels = len(label_classes)
    model = BertForSequenceClassification.from_pretrained(
        settings.biobert_base_model_name,
        config=model_config,
    )

    train_dataset = SymptomDataset(
        train_df['text'].tolist(),
        train_df['label'].tolist(),
        tokenizer,
        config.max_length,
    )
    eval_dataset = SymptomDataset(
        eval_df['text'].tolist(),
        eval_df['label'].tolist(),
        tokenizer,
        config.max_length,
    )

    output_dir = Path(settings.biobert_model_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = _build_training_arguments(output_dir, config)

    trainer = _build_trainer(model, training_args, train_dataset, eval_dataset, tokenizer)

    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    label_map = {str(index): label for index, label in enumerate(label_classes)}
    Path(settings.biobert_label_map_file).write_text(
        json.dumps(label_map, indent=2),
        encoding='utf-8',
    )

    print(f'BioBERT model saved to {output_dir}')
    print(f'Label mapping saved to {settings.biobert_label_map_file}')


if __name__ == '__main__':
    train()
