from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import Base, engine
from backend.routers import artworks, plates, papers, batches, dashboard, export

Base.metadata.create_all(bind=engine)

app = FastAPI(title="手工版画工作室管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artworks.router)
app.include_router(plates.router)
app.include_router(papers.router)
app.include_router(batches.router)
app.include_router(dashboard.router)
app.include_router(export.router)

@app.get("/")
def read_root():
    return {"message": "手工版画工作室管理平台 API 服务已启动"}
