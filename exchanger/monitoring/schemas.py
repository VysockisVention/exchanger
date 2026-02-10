from typing import Literal

from pydantic import BaseModel


class ReadyResponse(BaseModel):
    status: Literal["ok"]


class LiveResponse(BaseModel):
    status: Literal["ok"]
