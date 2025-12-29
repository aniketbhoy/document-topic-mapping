"""Relationship model for topic connections."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class Relationship(BaseModel):
    """Model representing a relationship between topics."""

    source: str = Field(..., description="Source topic ID")
    target: str = Field(..., description="Target topic ID")
    type: Literal["hierarchical", "cross_reference", "forward_reference", "backward_reference"] = Field(
        ..., description="Type of relationship"
    )
    status: Literal["valid", "broken", "ambiguous"] = Field(
        "valid", description="Status of the relationship"
    )
    context: Optional[str] = Field(None, description="Context where the relationship was found")
    severity: Optional[Literal["low", "medium", "high"]] = Field(
        None, description="Severity if relationship is broken or ambiguous"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source": "18",
                "target": "18.2",
                "type": "cross_reference",
                "status": "broken",
                "context": "As discussed in Topic 18.2...",
                "severity": "high"
            }
        }
