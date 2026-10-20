"""Pydantic models shared by the LangGraph nodes and the FastAPI layer."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

Priority = Literal["High", "Medium", "Low"]


class ExtractedTask(BaseModel):
    title: str = Field(description="Short, clear action-oriented task title")
    deadline: Optional[str] = Field(
        default=None,
        description="Deadline or time phrase from the text, e.g. 'tomorrow', "
                    "'today', 'next week'. Null if none was mentioned.",
    )


class ExtractionResult(BaseModel):
    tasks: List[ExtractedTask]


class PrioritizedTask(BaseModel):
    title: str
    deadline: Optional[str] = None
    priority: Priority = Field(description="High, Medium or Low")
    reason: str = Field(description="One short sentence explaining the priority")


class PrioritizationResult(BaseModel):
    tasks: List[PrioritizedTask]


class OrganizeRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)


class OrganizeResponse(BaseModel):
    tasks: List[PrioritizedTask]
    formatted: str
