from fastapi import FastAPI

from apps.api.routes.query import router as query_router


app = FastAPI(
    title="AI Business Analyst API",
    description="Backend API for natural-language analytics over the Olist warehouse.",
    version="0.2.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(query_router, prefix="/api")
