from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime
from datetime import datetime
from .session import Base

class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    inspector_id = Column(String, default="INSP-LM-408")
    shop_name = Column(String, nullable=True)
    shop_location = Column(String, nullable=True)
    selling_price = Column(Float, nullable=True)

    # Images
    original_image_path = Column(String, nullable=False)
    enhanced_image_path = Column(String, nullable=True)
    annotated_image_path = Column(String, nullable=True)

    # Extracted fields and confidence
    extracted_data = Column(JSON, nullable=False)
    ocr_confidence = Column(Float, default=0.0)

    # Compliance Engine results
    verdict = Column(String, nullable=False)  # PASS, FAIL, REVIEW
    rule_results = Column(JSON, nullable=False)
    violations = Column(JSON, nullable=False)
    review_reasons = Column(JSON, nullable=False)

    # Cryptographic & Blockchain Audit
    record_hash = Column(String, nullable=False)
    blockchain_block_index = Column(Integer, nullable=True)
    blockchain_block_hash = Column(String, nullable=True)

    # Tamper simulation tracking
    is_tampered = Column(Boolean, default=False)
    original_mrp_for_tamper_demo = Column(Float, nullable=True)

class BlockchainBlock(Base):
    __tablename__ = "blockchain_blocks"

    index = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=False)
    previous_hash = Column(String, nullable=False)
    current_hash = Column(String, nullable=False, unique=True)
    data_hash = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    nonce = Column(Integer, default=0)

class ManufacturerBatch(Base):
    __tablename__ = "manufacturer_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, unique=True, index=True, nullable=False)
    product_name = Column(String, nullable=False)
    manufacturer_name = Column(String, nullable=False)
    mrp = Column(Float, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    total_units = Column(Integer, default=100)

class UnitSerial(Base):
    __tablename__ = "unit_serials"

    id = Column(Integer, primary_key=True, index=True)
    serial_id = Column(String, unique=True, index=True, nullable=False)
    batch_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    manufacturer_name = Column(String, nullable=False)
    scan_count = Column(Integer, default=0)
    last_scanned_shop = Column(String, nullable=True)
    first_scanned_at = Column(DateTime, nullable=True)
    status = Column(String, default="GENUINE_UNSCANNED")  # GENUINE_UNSCANNED, VERIFIED_SCANNED, DUPLICATE_SUSPICIOUS
