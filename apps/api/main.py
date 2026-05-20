import logging
import sys
import os
import time
import sqlalchemy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apps.api.routes.query import router as query_router
from core_analytics.analytics.engine import analytics_engine
from infra.observability.logger import setup_logging
from infra.config.settings import get_settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Business Analyst API")

@app.on_event("startup")
async def startup_event():
    """Ensure the ops schema and prompt_performances table exist."""
    try:
        settings = get_settings()
        engine = sqlalchemy.create_engine(settings.database_url)
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text("""
                CREATE SCHEMA IF NOT EXISTS ops;
                CREATE TABLE IF NOT EXISTS ops.prompt_performances (
                    id SERIAL PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    estimated_tokens INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
        logger.info("Operational logging initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize operational logging: {e}")

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

def estimate_tokens(text: str) -> int:
    """Simple character-based token estimation (approx 4 chars per token)."""
    return len(text) // 4

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Executes the analysis and logs performance to the database."""
    start_time = time.time()
    status = "success"
    
    logger.info(f"Received analysis request: query='{request.query}'")
    
    try:
        result_data = await analytics_engine.run(request.query)
        # Check if the result contains an error summary
        if any(a.name == "Error" for a in result_data.get("artifacts", [])):
            status = "failed"
            
        return {
            "summary": [a.model_dump() for a in result_data["artifacts"]],
            "active_agents": result_data["active_agents"]
        }
    except Exception as e:
        status = "error"
        raise e
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        tokens = estimate_tokens(request.query)
        try:
            settings = get_settings()
            engine = sqlalchemy.create_engine(settings.database_url)
            with engine.begin() as conn:
                conn.execute(
                    sqlalchemy.text("""
                        INSERT INTO ops.prompt_performances (prompt, estimated_tokens, status, duration_ms) 
                        VALUES (:prompt, :tokens, :status, :duration)
                    """),
                    {"prompt": request.query, "tokens": tokens, "status": status, "duration": duration_ms}
                )
        except Exception as log_err:
            logger.error(f"Failed to log performance to DB: {log_err}")

@app.get("/connection")
async def get_connection():
    """Returns the database name for UI branding."""
    try:
        settings = get_settings()
        db_name = settings.database_url.split("/")[-1]
        formatted_name = db_name.replace("_", " ").replace("-", " ").title()
        return {"database": formatted_name}
    except Exception:
        return {"database": "Data Warehouse"}

@app.get("/health")
async def health():
    return {"status": "ok"}
