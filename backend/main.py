from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import review

app = FastAPI(title="PRify", version="1.0.0", description="AI PR Review Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review.router, prefix="/api", tags=["review"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
