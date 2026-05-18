import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add root to path so we can import our engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core_analytics.analytics.engine import analytics_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/analyze")
async def analyze(request: QueryRequest):
    result_data = await analytics_engine.run(request.query)
    return {
        "summary": [a.model_dump() for a in result_data["artifacts"]],
        "active_agents": result_data["active_agents"]
    }
