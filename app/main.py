from fastapi import FastAPI
from app.api.products import router as products_router

app = FastAPI(
    title="AI E-Commerce Shopping Assistant",
    description="AI-powered shopping and product recommendation assistant.",
    version="0.1.0",
)
app.include_router(products_router)


@app.get("/")
def root():
    return {
        "message": "AI E-Commerce Shopping Assistant API",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }