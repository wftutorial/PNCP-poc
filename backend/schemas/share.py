"""SEO-PLAYBOOK P6: Schemas for shareable viability analyses."""

from typing import Optional

from pydantic import BaseModel, Field


class ShareAnaliseRequest(BaseModel):
    """Request to create a shareable analysis link."""

    bid_id: str = Field(..., min_length=1)
    bid_title: str = Field(..., min_length=1, max_length=500)
    bid_orgao: Optional[str] = None
    bid_uf: Optional[str] = Field(None, max_length=2)
    bid_valor: Optional[float] = Field(None, ge=0)
    bid_modalidade: Optional[str] = None
    viability_score: int = Field(..., ge=0, le=100)
    viability_level: str = Field(..., pattern=r"^(alta|media|baixa)$")
    viability_factors: dict = Field(default_factory=dict)


class ShareAnaliseResponse(BaseModel):
    """Response with the shareable URL."""

    url: str
    hash: str


class SharedAnalisePublic(BaseModel):
    """Public view of a shared analysis (no user_id exposed)."""

    hash: str
    bid_id: str
    bid_title: str
    bid_orgao: Optional[str] = None
    bid_uf: Optional[str] = None
    bid_valor: Optional[float] = None
    bid_modalidade: Optional[str] = None
    viability_score: int
    viability_level: str
    viability_factors: dict
    view_count: int = 0
    created_at: str
