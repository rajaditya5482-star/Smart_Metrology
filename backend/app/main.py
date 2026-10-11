import os
import uuid
import shutil
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database.session import Base, engine, get_db
from .database.models import InspectionRecord, BlockchainBlock, ManufacturerBatch, UnitSerial
from .cv.preprocessor import ImagePreprocessor
from .ocr.ocr_engine import OCREngine
from .parser.extractor import DeclarationExtractor
from .rules.legal_engine import LegalMetrologyRuleEngine
from .blockchain.blockchain import BlockchainLedger, calculate_file_sha256, canonical_record_payload
from .reports.report_generator import PDFReportGenerator
from .counterfeit.counterfeit import CounterfeitExtension
from .demo.sample_data import create_sample_images, SAMPLE_DIR

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartMetrology API",
    description="AI-Powered Legal Metrology Compliance Inspection & Tamper-Evident Audit System",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports_output")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Mount uploads static directory for image serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Initialize modules
preprocessor = ImagePreprocessor(upload_dir=UPLOAD_DIR)
ocr_engine = OCREngine()
field_extractor = DeclarationExtractor()
rule_engine = LegalMetrologyRuleEngine()
pdf_generator = PDFReportGenerator(output_dir=REPORTS_DIR)

# Generate sample fixtures at startup
SAMPLE_FIXTURES = create_sample_images()

# Initialize genesis block and dummy counterfeit batches if needed
with next(get_db()) as db:
    ledger = BlockchainLedger(db)
    # Register demo batches if none exist
    if db.query(ManufacturerBatch).count() == 0:
        CounterfeitExtension.register_batch(
            batch_id="B2026-08",
            product_name="Royal Butter Cookies 500g",
            manufacturer_name="Royale Foods India Ltd",
            mrp=50.0,
            unit_count=10,
            prefix="ABC",
            db=db
        )
        CounterfeitExtension.register_batch(
            batch_id="B2026-09",
            product_name="Sunpure Refined Sunflower Oil 1L",
            manufacturer_name="Pure Agri Oils Ltd",
            mrp=140.0,
            unit_count=10,
            prefix="SUN",
            db=db
        )

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "SmartMetrology",
        "ocr_engine": "RapidOCR-ONNX",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/samples")
def get_sample_packages():
    """Returns pre-bundled test packages for 1-click inspection demonstrations."""
    results = []
    for s in SAMPLE_FIXTURES:
        rel_path = f"/uploads/sample_images/{s['filename']}"
        results.append({
            "id": s["id"],
            "name": s["name"],
            "image_url": rel_path,
            "filename": s["filename"],
            "expected_verdict": s["expected_verdict"],
            "description": s["description"],
            "default_selling_price": s["default_selling_price"]
        })
    return results

@app.post("/api/inspect")
async def run_inspection(
    file: Optional[UploadFile] = File(None),
    sample_filename: Optional[str] = Form(None),
    shop_name: Optional[str] = Form("Om Sai General Store"),
    shop_location: Optional[str] = Form("Karol Bagh, New Delhi"),
    selling_price: Optional[float] = Form(None),
    inspector_id: Optional[str] = Form("INSP-LM-DELHI-408"),
    db: Session = Depends(get_db)
):
    """
    Complete end-to-end Legal Metrology inspection pipeline:
    1. Image ingest & file hashing
    2. Computer vision preprocessing (CLAHE, denoise, blur check)
    3. RapidOCR text detection & bounding boxes
    4. Legal Metrology declaration parsing
    5. Rule engine evaluation (PASS / FAIL / REVIEW)
    6. SHA-256 fingerprint & blockchain block creation
    7. PDF report generation
    """
    inspection_uuid = f"INSP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # Determine image source
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        save_filename = f"orig_{uuid.uuid4().hex[:8]}{ext}"
        original_image_path = os.path.join(UPLOAD_DIR, save_filename)
        with open(original_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif sample_filename:
        sample_source = os.path.join(SAMPLE_DIR, sample_filename)
        if not os.path.exists(sample_source):
            raise HTTPException(status_code=404, detail="Sample image not found")
        save_filename = f"sample_copy_{uuid.uuid4().hex[:8]}.jpg"
        original_image_path = os.path.join(UPLOAD_DIR, save_filename)
        shutil.copy(sample_source, original_image_path)
    else:
        raise HTTPException(status_code=400, detail="Either file upload or sample_filename is required")

    # Step 1: Computer Vision Enhancement
    cv_res = preprocessor.enhance_image(original_image_path)
    enhanced_path = cv_res["enhanced_path"]

    # Step 2: RapidOCR Inference
    ocr_res = ocr_engine.extract(enhanced_path)

    # Step 3: Legal Metrology Field Extraction
    extracted_obj = field_extractor.extract_declarations(ocr_res)
    declarations = extracted_obj["declarations"]
    annotations = extracted_obj["annotations_to_draw"]

    # Step 4: Draw detected bounding boxes on image
    annotated_path = preprocessor.annotate_detections(original_image_path, annotations)

    # Step 5: Rule-Based Compliance Engine
    rule_res = rule_engine.evaluate(
        declarations=declarations,
        ocr_metadata=ocr_res,
        cv_metadata=cv_res,
        selling_price=selling_price
    )
    verdict = rule_res["verdict"]

    # Step 6: Cryptographic Blockchain Ledger
    image_hash = calculate_file_sha256(original_image_path)
    mrp_val = declarations.get("mrp", {}).get("value")
    net_val = declarations.get("net_quantity", {}).get("value")
    net_unit = declarations.get("net_quantity", {}).get("unit")
    now_dt = datetime.utcnow()
    timestamp_str = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    viol_str = json.dumps(rule_res["violations"], sort_keys=True) if rule_res["violations"] else ""

    canonical_payload = canonical_record_payload(
        inspection_id=inspection_uuid,
        timestamp=timestamp_str,
        inspector_id=inspector_id,
        shop_name=shop_name,
        image_hash=image_hash,
        mrp=mrp_val,
        net_qty=net_val,
        net_unit=net_unit,
        verdict=verdict,
        violations_summary=viol_str
    )

    ledger = BlockchainLedger(db)
    block = ledger.add_inspection_block(canonical_payload)

    # Step 7: Save to Database
    record = InspectionRecord(
        inspection_id=inspection_uuid,
        timestamp=now_dt,
        inspector_id=inspector_id,
        shop_name=shop_name,
        shop_location=shop_location,
        selling_price=selling_price,
        original_image_path=original_image_path,
        enhanced_image_path=enhanced_path,
        annotated_image_path=annotated_path,
        extracted_data=declarations,
        ocr_confidence=ocr_res.get("mean_confidence", 0.0),
        verdict=verdict,
        rule_results=rule_res["rule_results"],
        violations=rule_res["violations"],
        review_reasons=rule_res["review_reasons"],
        record_hash=block.data_hash,
        blockchain_block_index=block.index,
        blockchain_block_hash=block.current_hash,
        is_tampered=False
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Step 8: Generate PDF Report
    pdf_filename = f"report_{inspection_uuid}.pdf"
    pdf_dict = {
        "inspection_id": inspection_uuid,
        "timestamp": record.timestamp.strftime("%d-%b-%Y %H:%M:%S UTC"),
        "inspector_id": inspector_id,
        "shop_name": shop_name,
        "shop_location": shop_location,
        "selling_price": selling_price,
        "verdict": verdict,
        "original_image_path": original_image_path,
        "annotated_image_path": annotated_path,
        "extracted_data": declarations,
        "rule_results": rule_res["rule_results"],
        "record_hash": block.data_hash,
        "blockchain_block_index": block.index,
        "blockchain_block_hash": block.current_hash
    }
    pdf_generator.generate_inspection_report(pdf_dict, pdf_filename)

    # URLs for frontend
    orig_url = f"/uploads/{os.path.basename(original_image_path)}"
    enhanced_url = f"/uploads/{os.path.basename(enhanced_path)}"
    annotated_url = f"/uploads/{os.path.basename(annotated_path)}"
    pdf_url = f"/api/reports/{record.id}/pdf"

    return {
        "id": record.id,
        "inspection_id": inspection_uuid,
        "timestamp": record.timestamp.isoformat(),
        "inspector_id": inspector_id,
        "shop_name": shop_name,
        "shop_location": shop_location,
        "selling_price": selling_price,
        "verdict": verdict,
        "images": {
            "original": orig_url,
            "enhanced": enhanced_url,
            "annotated": annotated_url
        },
        "cv_metrics": {
            "blur_variance": cv_res["blur_variance"],
            "is_blurry": cv_res["is_blurry"]
        },
        "ocr": {
            "mean_confidence": ocr_res["mean_confidence"],
            "lines_detected": len(ocr_res["lines"]),
            "raw_text": ocr_res["full_text"]
        },
        "extracted_data": declarations,
        "rule_results": rule_res["rule_results"],
        "violations": rule_res["violations"],
        "review_reasons": rule_res["review_reasons"],
        "summary": {
            "total_rules": rule_res["total_rules_checked"],
            "passed": rule_res["passed_count"],
            "failed": rule_res["failed_count"],
            "review": rule_res["review_count"]
        },
        "blockchain": {
            "block_index": block.index,
            "block_hash": block.current_hash,
            "record_sha256": block.data_hash,
            "status": "RECORDED_IMMUTABLE"
        },
        "report_pdf_url": pdf_url
    }

@app.get("/api/records")
def list_records(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(InspectionRecord).order_by(InspectionRecord.timestamp.desc()).limit(limit).all()
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "inspection_id": r.inspection_id,
            "timestamp": r.timestamp.isoformat(),
            "inspector_id": r.inspector_id,
            "shop_name": r.shop_name,
            "verdict": r.verdict,
            "mrp": r.extracted_data.get("mrp", {}).get("value") if r.extracted_data else None,
            "net_quantity": f"{r.extracted_data.get('net_quantity', {}).get('value')} {r.extracted_data.get('net_quantity', {}).get('unit')}" if r.extracted_data else None,
            "record_hash": r.record_hash,
            "block_index": r.blockchain_block_index,
            "is_tampered": r.is_tampered,
            "thumbnail": f"/uploads/{os.path.basename(r.original_image_path)}" if r.original_image_path else None
        })
    return results

@app.get("/api/records/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    r = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "id": r.id,
        "inspection_id": r.inspection_id,
        "timestamp": r.timestamp.isoformat(),
        "inspector_id": r.inspector_id,
        "shop_name": r.shop_name,
        "shop_location": r.shop_location,
        "selling_price": r.selling_price,
        "verdict": r.verdict,
        "images": {
            "original": f"/uploads/{os.path.basename(r.original_image_path)}" if r.original_image_path else None,
            "enhanced": f"/uploads/{os.path.basename(r.enhanced_image_path)}" if r.enhanced_image_path else None,
            "annotated": f"/uploads/{os.path.basename(r.annotated_image_path)}" if r.annotated_image_path else None,
        },
        "extracted_data": r.extracted_data,
        "ocr_confidence": r.ocr_confidence,
        "rule_results": r.rule_results,
        "violations": r.violations,
        "review_reasons": r.review_reasons,
        "record_hash": r.record_hash,
        "block_index": r.blockchain_block_index,
        "block_hash": r.blockchain_block_hash,
        "is_tampered": r.is_tampered,
        "pdf_url": f"/api/reports/{r.id}/pdf"
    }

@app.post("/api/records/{record_id}/verify-tamper")
def verify_tamper(record_id: int, db: Session = Depends(get_db)):
    ledger = BlockchainLedger(db)
    res = ledger.verify_record_integrity(record_id)
    return res

@app.post("/api/records/{record_id}/simulate-tamper")
def simulate_tamper(record_id: int, fake_mrp: float = 35.0, db: Session = Depends(get_db)):
    ledger = BlockchainLedger(db)
    res = ledger.simulate_tamper(record_id, fake_mrp)
    return res

@app.post("/api/records/{record_id}/revert-tamper")
def revert_tamper(record_id: int, db: Session = Depends(get_db)):
    ledger = BlockchainLedger(db)
    res = ledger.revert_tamper(record_id)
    return res

@app.get("/api/reports/{record_id}/pdf")
def download_pdf(record_id: int, db: Session = Depends(get_db)):
    r = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")
    pdf_path = os.path.join(REPORTS_DIR, f"report_{r.inspection_id}.pdf")
    if not os.path.exists(pdf_path):
        # Regenerate if missing
        pdf_dict = {
            "inspection_id": r.inspection_id,
            "timestamp": r.timestamp.strftime("%d-%b-%Y %H:%M:%S UTC"),
            "inspector_id": r.inspector_id,
            "shop_name": r.shop_name,
            "shop_location": r.shop_location,
            "selling_price": r.selling_price,
            "verdict": r.verdict,
            "original_image_path": r.original_image_path,
            "annotated_image_path": r.annotated_image_path,
            "extracted_data": r.extracted_data,
            "rule_results": r.rule_results,
            "record_hash": r.record_hash,
            "blockchain_block_index": r.blockchain_block_index,
            "blockchain_block_hash": r.blockchain_block_hash
        }
        pdf_generator.generate_inspection_report(pdf_dict, f"report_{r.inspection_id}.pdf")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"LegalMetrology_{r.inspection_id}.pdf"
    )

@app.get("/api/blockchain/blocks")
def get_blockchain_blocks(db: Session = Depends(get_db)):
    ledger = BlockchainLedger(db)
    return ledger.get_recent_blocks(20)

@app.post("/api/counterfeit/register")
def register_product_batch(
    batch_id: str = Form(...),
    product_name: str = Form(...),
    manufacturer_name: str = Form(...),
    mrp: float = Form(...),
    unit_count: int = Form(10),
    prefix: str = Form("ABC"),
    db: Session = Depends(get_db)
):
    return CounterfeitExtension.register_batch(
        batch_id=batch_id,
        product_name=product_name,
        manufacturer_name=manufacturer_name,
        mrp=mrp,
        unit_count=unit_count,
        prefix=prefix,
        db=db
    )

@app.post("/api/counterfeit/verify")
def verify_product_serial(
    serial_id: str = Form(...),
    shop_name: str = Form("Metro Cash & Carry"),
    db: Session = Depends(get_db)
):
    return CounterfeitExtension.verify_serial(
        serial_id=serial_id,
        shop_name=shop_name,
        db=db
    )

@app.get("/api/counterfeit/batches")
def get_counterfeit_batches(db: Session = Depends(get_db)):
    return CounterfeitExtension.list_batches(db)

@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(InspectionRecord).count()
    passed = db.query(InspectionRecord).filter(InspectionRecord.verdict == "PASS").count()
    failed = db.query(InspectionRecord).filter(InspectionRecord.verdict == "FAIL").count()
    review = db.query(InspectionRecord).filter(InspectionRecord.verdict == "REVIEW").count()

    # Calculate compliance rate
    comp_rate = round((passed / total * 100), 1) if total > 0 else 0.0

    # Common violations count
    records = db.query(InspectionRecord).filter(InspectionRecord.verdict == "FAIL").all()
    violation_counts = {}
    for r in records:
        for v in (r.violations or []):
            title = v.get("title", "Other Violation")
            violation_counts[title] = violation_counts.get(title, 0) + 1

    top_violations = [{"title": k, "count": v} for k, v in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

    return {
        "total_inspections": total,
        "passed": passed,
        "failed": failed,
        "review": review,
        "compliance_rate": comp_rate,
        "top_violations": top_violations,
        "blocks_mined": db.query(BlockchainBlock).count()
    }
