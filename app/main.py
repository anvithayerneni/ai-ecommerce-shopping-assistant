import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.assistant import router as assistant_router
from app.api.products import router as products_router
from app.core.logging_config import configure_logging


configure_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI E-Commerce Shopping Assistant",
    description="AI-powered shopping and product recommendation assistant.",
    version="0.1.0",
)

app.include_router(products_router)
app.include_router(assistant_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled application error: %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )


@app.get("/")
def root():
    logger.info("Root endpoint requested")

    return {
        "message": "AI E-Commerce Shopping Assistant API",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy"
    }