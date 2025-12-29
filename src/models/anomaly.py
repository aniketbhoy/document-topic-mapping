"""Anomaly model for tracking structural issues."""

from typing import List, Literal
from pydantic import BaseModel, Field


class Anomaly(BaseModel):
    """Model representing a detected anomaly in document structure."""

    type: Literal[
        "missing_referenced_topic",
        "broken_cross_reference",
        "circular_reference",
        "numbering_gap",
        "duplicate_topic",
        "orphan_content",
        "ambiguous_boundary"
    ] = Field(..., description="Type of anomaly")
    location: str = Field(..., description="Location of the anomaly")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Severity level"
    )
    description: str = Field(..., description="Detailed description of the anomaly")
    resolution_strategies: List[str] = Field(
        default_factory=list, description="Possible resolution strategies"
    )
    affected_topics: List[str] = Field(
        default_factory=list, description="Topics affected by this anomaly"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "missing_referenced_topic",
                "location": "18 → 18.2",
                "severity": "high",
                "description": "Topic 18 references 18.2, which does not exist",
                "resolution_strategies": [
                    "Check if 18.3 should be renumbered to 18.2",
                    "Search for unnumbered content between 18.1 and 18.3"
                ],
                "affected_topics": ["18", "18.1", "18.3"]
            }
        }
