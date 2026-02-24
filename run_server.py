"""
Startup script to run the API server.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from src.config.config import API_HOST, API_PORT
    
    print("=" * 60)
    print("AI-Powered Nutrition & Wellness Tracking System")
    print("=" * 60)
    print(f"\nStarting API server on http://{API_HOST}:{API_PORT}")
    print(f"\nAPI Documentation:")
    print(f"  - Swagger UI: http://{API_HOST}:{API_PORT}/api/docs")
    print(f"  - ReDoc: http://{API_HOST}:{API_PORT}/api/redoc")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
