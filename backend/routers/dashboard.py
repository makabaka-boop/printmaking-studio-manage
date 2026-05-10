from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from models import Artwork, PrintBatch, Paper
from schemas import DashboardPieItem, DashboardLineItem, DashboardWasteItem, PaperAlertItem

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/pie", response_model=list[DashboardPieItem])
def pie_data(db: Session = Depends(get_db)):
    rows = db.query(Artwork.print_type, func.count(Artwork.id)).group_by(Artwork.print_type).all()
    return [DashboardPieItem(name=r[0], value=r[1]) for r in rows]


@router.get("/line", response_model=list[DashboardLineItem])
def line_data(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    result = []
    for i in range(2, -1, -1):
        m = now - timedelta(days=i * 30)
        month_str = m.strftime("%Y-%m")
        count = db.query(func.count(PrintBatch.id)).filter(
            func.strftime("%Y-%m", PrintBatch.date) == month_str
        ).scalar() or 0
        result.append(DashboardLineItem(month=month_str, count=count))
    return result


@router.get("/waste", response_model=list[DashboardWasteItem])
def waste_data(db: Session = Depends(get_db)):
    rows = db.query(
        Artwork.name,
        func.sum(PrintBatch.waste_count).label("waste"),
        func.sum(PrintBatch.trial_count + PrintBatch.official_count + PrintBatch.waste_count).label("total"),
    ).join(PrintBatch, Artwork.id == PrintBatch.artwork_id).group_by(Artwork.id).all()
    items = []
    for r in rows:
        if r.total > 0:
            items.append(DashboardWasteItem(artwork_name=r.name, waste_rate=round(r.waste / r.total * 100, 2)))
    items.sort(key=lambda x: x.waste_rate, reverse=True)
    return items[:10]


@router.get("/alerts", response_model=list[PaperAlertItem])
def alerts_data(db: Session = Depends(get_db)):
    return db.query(Paper).filter(Paper.stock <= Paper.threshold).all()
