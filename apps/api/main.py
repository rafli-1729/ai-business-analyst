import logging
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apps.api.routes.query import router as query_router
from core_analytics.analytics.engine import analytics_engine
from infra.observability.logger import setup_logging

# Setup logging
setup_logging()

app = FastAPI(title="AI Business Analyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include refactored query router
app.include_router(query_router)

class AnalyzeRequest(BaseModel):
    query: str

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Legacy endpoint for compatibility."""
    result_data = await analytics_engine.run(request.query)
    return {
        "summary": [a.model_dump() for a in result_data["artifacts"]],
        "active_agents": result_data["active_agents"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
