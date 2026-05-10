from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import Workbook
from io import BytesIO
from database import get_db
from models import Artwork, PrintBatch, BatchPlateUsage, Plate

router = APIRouter(prefix="/export", tags=["导出"])


@router.get("/edition/{artwork_id}")
def export_edition(artwork_id: int, db: Session = Depends(get_db)):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")

    batches = db.query(PrintBatch).filter(PrintBatch.artwork_id == artwork_id).order_by(PrintBatch.date).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Edition台账"

    ws.append(["作品名", "版种", "成品尺寸", "计划版数", "剩余可售版数", "签名规则"])
    ws.append([artwork.name, artwork.print_type, artwork.size, artwork.planned_edition, artwork.remaining_edition, artwork.signature_rule])
    ws.append([])
    ws.append(["批次ID", "日期", "试印张数", "正印张数", "废张数", "纸张消耗", "使用版次", "备注"])

    for b in batches:
        plate_ids = [u.plate_id for u in b.plate_usages]
        plates = db.query(Plate).filter(Plate.id.in_(plate_ids)).all() if plate_ids else []
        plate_info = ", ".join([f"第{p.color_order}色版" for p in plates])
        ws.append([b.id, str(b.date), b.trial_count, b.official_count, b.waste_count, b.paper_consumed, plate_info, b.note or ""])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=edition_{artwork_id}.xlsx"},
    )
