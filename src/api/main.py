"""
Main FastAPI application.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from src.config.database import init_db
from src.config.config import API_HOST, API_PORT, LOG_LEVEL, LOG_FILE

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Nutrition & Wellness Tracking API",
    description="Comprehensive health and wellness platform with food recognition, activity tracking, and AI-powered recommendations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application...")
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI-Powered Nutrition & Wellness Tracking API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2026-01-21T10:21:18+05:30"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


# Import and include routers
from src.api.routes import auth_routes, user_routes, food_routes, activity_routes, chat_routes, calorie_routes

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(food_routes.router, prefix="/api/food", tags=["Food & Nutrition"])
app.include_router(activity_routes.router, prefix="/api/activity", tags=["Activity & Wellness"])
app.include_router(chat_routes.router, prefix="/api/chat", tags=["AI Chat"])
app.include_router(calorie_routes.router, prefix="/api/calorie", tags=["Bangalore Calorie Tracker"])


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
