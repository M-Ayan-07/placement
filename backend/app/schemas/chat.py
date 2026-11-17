from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    title: str = Field(default="Placement Guidance Session", max_length=200)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    started_at: datetime
    messages: list[ChatMessageOut] = []


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class SendMessageResponse(BaseModel):
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut

