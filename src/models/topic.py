"""Topic model for representing document topics."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class TopicPosition(BaseModel):
    """Position metadata for a topic in the document."""
    start: int = Field(..., description="Start position in the document")
    end: int = Field(..., description="End position in the document")


class Topic(BaseModel):
    """Model representing a document topic."""

    id: str = Field(..., description="Topic ID (e.g., '18.3')")
    title: str = Field(..., description="Topic title")
    content: str = Field(..., description="Topic content")
    parent: Optional[str] = Field(None, description="Parent topic ID")
    children: List[str] = Field(default_factory=list, description="List of child topic IDs")
    cross_references: List[str] = Field(default_factory=list, description="Topics referenced by this topic")
    forward_references: List[str] = Field(default_factory=list, description="References to later topics")
    backward_references: List[str] = Field(default_factory=list, description="References to earlier topics")
    position: Optional[TopicPosition] = Field(None, description="Position in document")
    confidence: float = Field(0.95, ge=0.0, le=1.0, description="Confidence score for topic detection")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "18.3",
                "title": "Risk Assessment Procedures",
                "content": "This section describes...",
                "parent": "18",
                "children": [],
                "cross_references": ["8.2", "12.1"],
                "forward_references": ["22.1"],
                "backward_references": ["30.4"],
                "position": {"start": 1234, "end": 1567},
                "confidence": 0.95
            }
        }
