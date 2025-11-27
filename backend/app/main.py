from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, comics, ratings, recommendations, images, stats

app = FastAPI(
    title="AI Comic Recommender API",
    description="A FastAPI backend for comic book recommendations",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(comics.router, prefix="/api/comics", tags=["comics"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["ratings"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(stats.router, prefix="/api/stats", tags=["statistics"])


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    from .core.database import engine
    from .models import Base
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Comic Recommender API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}