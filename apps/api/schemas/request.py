from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=800)
    row_limit: int = Field(default=100, ge=1, le=500)
    refresh: bool = False
