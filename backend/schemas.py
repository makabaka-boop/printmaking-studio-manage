from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class PlateCreate(BaseModel):
    artwork_id: int
    color_order: int
    ink_ratio_note: Optional[str] = None
    is_finalized: bool = False


class PlateOut(PlateCreate):
    id: int
    class Config:
        from_attributes = True


class ArtworkCreate(BaseModel):
    name: str
    print_type: str
    size: Optional[str] = None
    planned_edition: int
    signature_rule: Optional[str] = None


class ArtworkOut(ArtworkCreate):
    id: int
    remaining_edition: int
    created_at: datetime
    plates: List[PlateOut] = []
    class Config:
        from_attributes = True


class PaperCreate(BaseModel):
    name: str
    gram_weight: float
    size: str
    stock: int = 0
    unit_cost: float = 0
    threshold: int = 10


class PaperOut(PaperCreate):
    id: int
    class Config:
        from_attributes = True


class BatchPlateUsageCreate(BaseModel):
    plate_id: int


class BatchPlateUsageOut(BatchPlateUsageCreate):
    id: int
    batch_id: int
    class Config:
        from_attributes = True


class PrintBatchCreate(BaseModel):
    artwork_id: int
    date: date
    trial_count: int = 0
    official_count: int = 0
    waste_count: int = 0
    paper_id: int
    paper_consumed: int = 0
    note: Optional[str] = None
    plate_ids: List[int] = []


class PrintBatchOut(BaseModel):
    id: int
    artwork_id: int
    date: date
    trial_count: int
    official_count: int
    waste_count: int
    paper_id: int
    paper_name_snapshot: str = ""
    paper_consumed: int
    note: Optional[str] = None
    created_at: datetime
    plate_usages: List[BatchPlateUsageOut] = []
    class Config:
        from_attributes = True


class DashboardPieItem(BaseModel):
    name: str
    value: int


class DashboardLineItem(BaseModel):
    month: str
    count: int


class DashboardWasteItem(BaseModel):
    artwork_name: str
    waste_rate: float


class PaperAlertItem(BaseModel):
    id: int
    name: str
    stock: int
    threshold: int
