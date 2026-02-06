from __future__ import annotations

from pydantic import BaseModel


class ReadyResponse(BaseModel):
    ready: bool


class LiveResponse(BaseModel):
    status: bool
