from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=120)


class ChatSummaryResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    language: str = Field(default='en', min_length=2, max_length=10)


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    user_id: str
    role: Literal['user', 'assistant']
    text: str
    language: str
    voice_path: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

    model_config = ConfigDict(from_attributes=True)
