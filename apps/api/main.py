from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routes.query import router as query_router


app = FastAPI(
    title="AI Business Analyst API",
    description="Backend API for natural-language analytics over the Olist warehouse.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-business-analyst-sand.vercel.app/"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(query_router, prefix="/api")
