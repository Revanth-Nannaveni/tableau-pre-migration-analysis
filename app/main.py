from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.routes.analysis import router as analysis_router
import logging
from config import DEBUG, ALLOWED_ORIGINS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tableau Pre-Migration Analysis API",
    description="Comprehensive analysis tool for Tableau to Power BI migrations",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)

# Include routers
app.include_router(analysis_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Tableau Pre-Migration Analysis API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Tableau Pre-Migration Analysis API shutting down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tableau Pre-Migration Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "discover": "/api/v1/analysis/discover-workbooks",
            "analyze": "/api/v1/analysis/analyze-workbook",
            "upload": "/api/v1/analysis/upload-workbook",
            "health": "/api/v1/analysis/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
