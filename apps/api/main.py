from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routes.query import router as query_router


app = FastAPI(
    title="AI Business Analyst API",
    description="Backend API for natural-language analytics over the Olist warehouse.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response()

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(query_router, prefix="/api")
