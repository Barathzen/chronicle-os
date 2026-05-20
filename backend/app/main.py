from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth as auth_router
from app.api.routes import embeddings as embeddings_router

app = FastAPI(
    title="ChronicleOS",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "ChronicleOS API running"}


# include routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
from app.api.routes import documents as docs_router
app.include_router(docs_router.router, prefix="/documents", tags=["documents"])
app.include_router(embeddings_router.router, prefix="", tags=["embeddings"])