from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

import models
import schemas
import crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="版画工作室管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "版画工作室管理系统 API"}


@app.get("/artworks/", response_model=List[schemas.Artwork])
def read_artworks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_artworks(db, skip=skip, limit=limit)


@app.get("/artworks/{artwork_id}", response_model=schemas.Artwork)
def read_artwork(artwork_id: int, db: Session = Depends(get_db)):
    db_artwork = crud.get_artwork(db, artwork_id=artwork_id)
    if db_artwork is None:
        raise HTTPException(status_code=404, detail="作品不存在")
    return db_artwork


@app.post("/artworks/", response_model=schemas.Artwork)
def create_artwork(artwork: schemas.ArtworkCreate, db: Session = Depends(get_db)):
    return crud.create_artwork(db=db, artwork=artwork)


@app.delete("/artworks/{artwork_id}")
def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    success = crud.delete_artwork(db, artwork_id=artwork_id)
    if not success:
        raise HTTPException(status_code=404, detail="作品不存在")
    return {"message": "删除成功"}


@app.get("/plates/", response_model=List[schemas.Plate])
def read_plates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_plates(db, skip=skip, limit=limit)


@app.get("/plates/artwork/{artwork_id}", response_model=List[schemas.Plate])
def read_plates_by_artwork(artwork_id: int, db: Session = Depends(get_db)):
    return crud.get_plates_by_artwork(db, artwork_id=artwork_id)


@app.post("/plates/", response_model=schemas.Plate)
def create_plate(plate: schemas.PlateCreate, db: Session = Depends(get_db)):
    return crud.create_plate(db=db, plate=plate)


@app.put("/plates/{plate_id}", response_model=schemas.Plate)
def update_plate(plate_id: int, plate: schemas.PlateUpdate, db: Session = Depends(get_db)):
    db_plate = crud.update_plate(db, plate_id=plate_id, plate_update=plate)
    if db_plate is None:
        raise HTTPException(status_code=404, detail="版次不存在")
    return db_plate


@app.delete("/plates/{plate_id}")
def delete_plate(plate_id: int, db: Session = Depends(get_db)):
    success = crud.delete_plate(db, plate_id=plate_id)
    if not success:
        raise HTTPException(status_code=404, detail="版次不存在")
    return {"message": "删除成功"}


@app.get("/papers/", response_model=List[schemas.Paper])
def read_papers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_papers(db, skip=skip, limit=limit)


@app.get("/papers/low-stock/", response_model=List[schemas.Paper])
def read_low_stock_papers(db: Session = Depends(get_db)):
    return crud.get_low_stock_papers(db)


@app.get("/papers/{paper_id}", response_model=schemas.Paper)
def read_paper(paper_id: int, db: Session = Depends(get_db)):
    db_paper = crud.get_paper(db, paper_id=paper_id)
    if db_paper is None:
        raise HTTPException(status_code=404, detail="纸张不存在")
    return db_paper


@app.post("/papers/", response_model=schemas.Paper)
def create_paper(paper: schemas.PaperCreate, db: Session = Depends(get_db)):
    return crud.create_paper(db=db, paper=paper)


@app.put("/papers/{paper_id}", response_model=schemas.Paper)
def update_paper(paper_id: int, paper: schemas.PaperUpdate, db: Session = Depends(get_db)):
    db_paper = crud.update_paper(db, paper_id=paper_id, paper_update=paper)
    if db_paper is None:
        raise HTTPException(status_code=404, detail="纸张不存在")
    return db_paper


@app.delete("/papers/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    success = crud.delete_paper(db, paper_id=paper_id)
    if not success:
        raise HTTPException(status_code=404, detail="纸张不存在")
    return {"message": "删除成功"}


@app.get("/batches/", response_model=List[schemas.PrintBatch])
def read_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_print_batches(db, skip=skip, limit=limit)


@app.get("/batches/artwork/{artwork_id}", response_model=List[schemas.PrintBatch])
def read_batches_by_artwork(artwork_id: int, db: Session = Depends(get_db)):
    return crud.get_print_batches_by_artwork(db, artwork_id=artwork_id)


@app.post("/batches/", response_model=schemas.PrintBatch)
def create_batch(batch: schemas.PrintBatchCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_print_batch(db=db, batch=batch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/batches/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    success = crud.delete_print_batch(db, batch_id=batch_id)
    if not success:
        raise HTTPException(status_code=404, detail="批次不存在")
    return {"message": "删除成功"}


@app.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@app.get("/dashboard/print-types", response_model=List[schemas.PrintTypeStats])
def get_print_types(db: Session = Depends(get_db)):
    return crud.get_print_type_stats(db)


@app.get("/dashboard/monthly-batches", response_model=List[schemas.MonthlyBatchStats])
def get_monthly_batches(db: Session = Depends(get_db)):
    return crud.get_monthly_batch_stats(db)


@app.get("/dashboard/waste-rates", response_model=List[schemas.WasteRateStats])
def get_waste_rates(db: Session = Depends(get_db)):
    return crud.get_waste_rate_stats(db)


@app.get("/export/edition/{artwork_id}")
def export_edition_excel(artwork_id: int, db: Session = Depends(get_db)):
    artwork = crud.get_artwork(db, artwork_id=artwork_id)
    if artwork is None:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    batches = crud.get_print_batches_by_artwork(db, artwork_id=artwork_id)
    plates = crud.get_plates_by_artwork(db, artwork_id=artwork_id)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Edition台账"
    
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    ws["A1"] = "作品信息"
    ws["A1"].font = Font(bold=True, size=14)
    
    ws["A3"] = "作品名称"
    ws["B3"] = artwork.name
    ws["A4"] = "版种"
    ws["B4"] = artwork.print_type
    ws["A5"] = "成品尺寸"
    ws["B5"] = artwork.finished_size or ""
    ws["A6"] = "计划印数"
    ws["B6"] = artwork.planned_edition
    ws["A7"] = "已印制数"
    ws["B7"] = artwork.sold_count
    ws["A8"] = "剩余可售"
    ws["B8"] = artwork.remaining_edition
    ws["A9"] = "签名规则"
    ws["B9"] = artwork.signature_rule or ""
    
    row = 11
    ws[f"A{row}"] = "版次信息"
    ws[f"A{row}"].font = Font(bold=True, size=14)
    row += 2
    
    headers = ["色版号", "油墨配比", "是否定稿", "备注"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    row += 1
    
    for plate in plates:
        ws.cell(row=row, column=1, value=plate.color_number)
        ws.cell(row=row, column=2, value=plate.ink_ratio or "")
        ws.cell(row=row, column=3, value="是" if plate.is_finalized else "否")
        ws.cell(row=row, column=4, value=plate.notes or "")
        row += 1
    
    row += 2
    ws[f"A{row}"] = "印制批次"
    ws[f"A{row}"].font = Font(bold=True, size=14)
    row += 2
    
    headers = ["日期", "使用版次", "试印张数", "正印张数", "废张数", "用纸张数", "备注"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    row += 1
    
    for batch in batches:
        ws.cell(row=row, column=1, value=batch.print_date.strftime("%Y-%m-%d"))
        ws.cell(row=row, column=2, value=batch.plate_ids or "")
        ws.cell(row=row, column=3, value=batch.trial_print_count)
        ws.cell(row=row, column=4, value=batch.final_print_count)
        ws.cell(row=row, column=5, value=batch.waste_count)
        ws.cell(row=row, column=6, value=batch.paper_used)
        ws.cell(row=row, column=7, value=batch.notes or "")
        row += 1
    
    for col in range(1, 10):
        ws.column_dimensions[chr(64 + col)].width = 15
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"{artwork.name}_edition台账.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename.encode('utf-8').decode('latin-1')}"}
    )
