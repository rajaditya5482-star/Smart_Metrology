import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from backend.app.database.session import SessionLocal, Base, engine
from backend.app.database.models import InspectionRecord, BlockchainBlock
from backend.app.cv.preprocessor import ImagePreprocessor
from backend.app.ocr.ocr_engine import OCREngine
from backend.app.parser.extractor import DeclarationExtractor
from backend.app.rules.legal_engine import LegalMetrologyRuleEngine
from backend.app.blockchain.blockchain import BlockchainLedger
from backend.app.demo.sample_data import create_sample_images, SAMPLE_DIR
from backend.app.reports.report_generator import PDFReportGenerator

def test_full_pipeline():
    print("1. Creating sample images...")
    samples = create_sample_images()
    assert len(samples) >= 5, "Sample images not generated"
    print(f"Generated {len(samples)} samples successfully.")

    print("2. Initializing database and tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("3. Testing OCR Engine & Preprocessor on Compliant Sample...")
    prep = ImagePreprocessor(upload_dir=os.path.join(os.path.dirname(SAMPLE_DIR)))
    ocr = OCREngine()
    extractor = DeclarationExtractor()
    rules = LegalMetrologyRuleEngine()

    p1_path = samples[0]["path"] # Compliant biscuits
    cv_res = prep.enhance_image(p1_path)
    print(f"CV Enhancement completed: blur_var={cv_res['blur_variance']}, is_blurry={cv_res['is_blurry']}")

    ocr_res = ocr.extract(cv_res["enhanced_path"])
    print(f"OCR extracted {len(ocr_res['lines'])} lines, mean confidence={ocr_res['mean_confidence']}")

    extracted = extractor.extract_declarations(ocr_res)
    decl = extracted["declarations"]
    print(f"Extracted MRP: {decl['mrp']}")
    print(f"Extracted Net Qty: {decl['net_quantity']}")
    print(f"Extracted Date: {decl['mfg_date']}")

    eval_res = rules.evaluate(decl, ocr_res, cv_res)
    print(f"Rule Engine Verdict for Sample 1: {eval_res['verdict']}")
    print(f"Passed rules: {eval_res['passed_count']}, Failed: {eval_res['failed_count']}")

    print("4. Testing Blockchain & Tamper Detection...")
    ledger = BlockchainLedger(db)
    blocks = ledger.get_recent_blocks()
    print(f"Blockchain active, genesis block count={len(blocks)}")

    print("5. Testing Missing MRP Sample (Sample 2)...")
    p2_path = samples[1]["path"]
    ocr_res2 = ocr.extract(p2_path)
    decl2 = extractor.extract_declarations(ocr_res2)["declarations"]
    eval_res2 = rules.evaluate(decl2, ocr_res2, {"is_blurry": False})
    print(f"Sample 2 Verdict: {eval_res2['verdict']} (Violations: {[v['title'] for v in eval_res2['violations']]})")
    assert eval_res2['verdict'] == 'FAIL', "Sample 2 should FAIL due to missing MRP"

    print("6. Testing Overpricing Rule...")
    eval_overprice = rules.evaluate(decl, ocr_res, cv_res, selling_price=75.0)
    print(f"Overprice test (MRP=50, Shop Price=75): Verdict={eval_overprice['verdict']}")
    assert any("Overpricing" in v['title'] for v in eval_overprice['violations']), "Overpricing should be caught"

    print("\nALL BACKEND CORE PIPELINE TESTS PASSED!")
    db.close()

if __name__ == "__main__":
    test_full_pipeline()
