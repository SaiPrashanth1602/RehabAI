import time
from datetime import datetime
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.firebase import get_firestore_db

# FIXED: Ensure all structural route modules are imported cleanly
from backend.routes import patients, sessions, dashboard

app = FastAPI(
    title="RehabAI Backend API",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware for production readiness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Application Route Modules with API V1 prefix ("/api/v1")
app.include_router(patients.router, prefix=settings.API_V1_STR)
app.include_router(sessions.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
async def root():
    return {"message": "RehabAI Backend Running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    # Enforce standard string reload layout matching production specifications
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)