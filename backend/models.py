from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Artwork(Base):
    __tablename__ = "artworks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    print_type = Column(String(50), nullable=False)
    size = Column(String(100))
    planned_edition = Column(Integer, nullable=False)
    signature_rule = Column(String(200))
    remaining_edition = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    plates = relationship("Plate", back_populates="artwork", cascade="all, delete-orphan")
    batches = relationship("PrintBatch", back_populates="artwork", cascade="all, delete-orphan")


class Plate(Base):
    __tablename__ = "plates"
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    color_order = Column(Integer, nullable=False)
    ink_ratio_note = Column(Text)
    is_finalized = Column(Boolean, default=False)
    artwork = relationship("Artwork", back_populates="plates")


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    gram_weight = Column(Float, nullable=False)
    size = Column(String(100), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    unit_cost = Column(Float, nullable=False, default=0)
    threshold = Column(Integer, nullable=False, default=10)


class PrintBatch(Base):
    __tablename__ = "print_batches"
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    date = Column(Date, nullable=False)
    trial_count = Column(Integer, default=0)
    official_count = Column(Integer, default=0)
    waste_count = Column(Integer, default=0)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    paper_name_snapshot = Column(String(200), nullable=False, default="")
    paper_consumed = Column(Integer, nullable=False, default=0)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    artwork = relationship("Artwork", back_populates="batches")
    paper = relationship("Paper")
    plate_usages = relationship("BatchPlateUsage", back_populates="batch", cascade="all, delete-orphan")


class BatchPlateUsage(Base):
    __tablename__ = "batch_plate_usages"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("print_batches.id"), nullable=False)
    plate_id = Column(Integer, ForeignKey("plates.id"), nullable=False)
    batch = relationship("PrintBatch", back_populates="plate_usages")
    plate = relationship("Plate")
