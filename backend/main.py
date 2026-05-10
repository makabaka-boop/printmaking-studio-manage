from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import artworks, papers, batches, dashboard, export

Base.metadata.create_all(bind=engine)

app = FastAPI(title="版画工作室管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artworks.router)
app.include_router(papers.router)
app.include_router(batches.router)
app.include_router(dashboard.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"message": "版画工作室管理平台 API"}
