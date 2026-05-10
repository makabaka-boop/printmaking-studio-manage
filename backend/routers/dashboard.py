from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict
from backend.database.database import get_db
from backend.models import models

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_artworks = db.query(func.count(models.Artwork.id)).scalar()
    total_batches = db.query(func.count(models.PrintBatch.id)).scalar()
    total_papers = db.query(func.count(models.Paper.id)).scalar()
    low_stock_count = db.query(func.count(models.Paper.id)).filter(models.Paper.stock < models.Paper.threshold).scalar()
    
    return {
        "total_artworks": total_artworks or 0,
        "total_batches": total_batches or 0,
        "total_papers": total_papers or 0,
        "low_stock_count": low_stock_count or 0
    }

@router.get("/print-type-chart")
def get_print_type_chart(db: Session = Depends(get_db)):
    result = db.query(
        models.Artwork.print_type,
        func.count(models.Artwork.id)
    ).group_by(models.Artwork.print_type).all()
    
    data = []
    for print_type, count in result:
        data.append({"name": print_type, "value": count})
    
    return data

@router.get("/recent-batches-chart")
def get_recent_batches_chart(db: Session = Depends(get_db)):
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    
    result = db.query(
        func.date(models.PrintBatch.print_date),
        func.count(models.PrintBatch.id)
    ).filter(
        models.PrintBatch.print_date >= three_months_ago
    ).group_by(
        func.date(models.PrintBatch.print_date)
    ).order_by(
        func.date(models.PrintBatch.print_date)
    ).all()
    
    dates = []
    counts = []
    for date_str, count in result:
        dates.append(date_str)
        counts.append(count)
    
    return {"dates": dates, "counts": counts}

@router.get("/waste-rate-chart")
def get_waste_rate_chart(db: Session = Depends(get_db)):
    batches = db.query(models.PrintBatch).all()
    
    artwork_stats = {}
    for batch in batches:
        if batch.artwork_id not in artwork_stats:
            artwork_stats[batch.artwork_id] = {
                "name": batch.artwork.name,
                "total_waste": 0,
                "total_prints": 0
            }
        artwork_stats[batch.artwork_id]["total_waste"] += batch.waste_prints
        artwork_stats[batch.artwork_id]["total_prints"] += batch.good_prints + batch.test_prints + batch.waste_prints
    
    data = []
    for artwork_id, stats in artwork_stats.items():
        if stats["total_prints"] > 0:
            waste_rate = (stats["total_waste"] / stats["total_prints"]) * 100
            data.append({"name": stats["name"], "waste_rate": round(waste_rate, 2)})
    
    data.sort(key=lambda x: x["waste_rate"], reverse=True)
    return data[:10]

@router.get("/low-stock-papers")
def get_low_stock_papers(db: Session = Depends(get_db)):
    papers = db.query(models.Paper).filter(models.Paper.stock < models.Paper.threshold).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "weight": p.weight,
            "size": p.size,
            "stock": p.stock,
            "threshold": p.threshold,
            "deficit": p.threshold - p.stock
        }
        for p in papers
    ]
