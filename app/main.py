import logging
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.models.loader import ModelLoader
from app.routers import movies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Create FastAPI app with metadata
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(f"Request to {request.url.path} took {process_time:.4f}s")
        return response
    except Exception as e:
        logger.error(f"Request to {request.url.path} failed: {str(e)}")
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "path": request.url.path, "process_time": process_time}
        )

# Include routers
app.include_router(movies.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": request.url.path}
    )

@app.on_event("startup")
async def startup_event():
    """Initialize models and data on application startup."""
    logger.info("Starting movie recommendation API")
    try:
        model_loader = ModelLoader()
        model_loader.load_models()
        model_loader.load_dataset()
        logger.info("API startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Allow the app to start even if models fail to load - they can be loaded later

@app.get("/", tags=["status"])
async def root():
    """Root endpoint - check if API is running."""
    return {"status": "online", "api_version": settings.API_VERSION}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )