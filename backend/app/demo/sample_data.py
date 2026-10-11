import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads", "sample_images")

def create_sample_images():
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    samples = []

    # -------------------------------------------------------------
    # 1. Compliant Butter Cookies (PASS)
    # -------------------------------------------------------------
    img1 = Image.new("RGB", (800, 600), color=(248, 246, 240))
    d1 = ImageDraw.Draw(img1)
    
    # Outer decorative packaging border
    d1.rectangle([(20, 20), (780, 580)], outline=(180, 140, 60), width=4)
    d1.rectangle([(26, 26), (774, 574)], outline=(220, 180, 100), width=2)

    # Brand & Commodity
    d1.text((50, 45), "ROYAL HERITAGE", fill=(120, 40, 20))
    d1.text((50, 80), "ROYAL BUTTER COOKIES", fill=(20, 20, 20))
    d1.line([(50, 130), (750, 130)], fill=(200, 160, 80), width=2)

    # Declarations Panel
    d1.rectangle([(50, 150), (750, 550)], fill=(255, 255, 255), outline=(200, 200, 200), width=1)
    
    lines_p1 = [
        "STATUTORY DECLARATIONS (PACKAGED COMMODITIES RULES):",
        "",
        "Generic Name: Butter Cookies",
        "Net Quantity: 500 g",
        "MRP: Rs. 50.00 (Inclusive of all taxes)",
        "Date of Mfg: 08/2026",
        "Manufactured and Packed By:",
        "Royale Foods India Ltd, Plot 42, Industrial Area,",
        "Okhla Phase-III, New Delhi - 110020",
        "Consumer Care Cell: 1800-111-2222 | care@royalefoods.com",
        "Country of Origin: Made in India"
    ]
    y = 170
    for line in lines_p1:
        color = (15, 23, 42) if "STATUTORY" not in line else (30, 58, 138)
        d1.text((70, y), line, fill=color)
        y += 32

    p1_path = os.path.join(SAMPLE_DIR, "sample_1_compliant_biscuits.jpg")
    img1.save(p1_path, quality=95)
    samples.append({
        "id": "sample_1",
        "name": "Compliant Butter Cookies (Expected: PASS)",
        "path": p1_path,
        "filename": "sample_1_compliant_biscuits.jpg",
        "expected_verdict": "PASS",
        "description": "All 7 mandatory declarations present with correct metric unit ('500 g') and tax inclusivity statement.",
        "default_selling_price": 50.0
    })

    # -------------------------------------------------------------
    # 2. Missing MRP Face Cream (FAIL)
    # -------------------------------------------------------------
    img2 = Image.new("RGB", (800, 600), color=(240, 247, 244))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([(20, 20), (780, 580)], outline=(46, 117, 89), width=3)
    d2.text((50, 50), "NATURA HERBALS", fill=(46, 117, 89))
    d2.text((50, 90), "GLOW AYURVEDIC NIGHT CREAM", fill=(10, 10, 10))
    d2.line([(50, 135), (750, 135)], fill=(120, 180, 150), width=2)

    d2.rectangle([(50, 155), (750, 545)], fill=(255, 255, 255), outline=(210, 220, 215), width=1)
    lines_p2 = [
        "MANDATORY PRODUCT DETAILS:",
        "",
        "Generic Name: Facial Cosmetic Cream",
        "Net Quantity: 50 g",
        "Date of Mfg: 06/2026",
        "Manufactured by: Herbal Care Laboratories, Industrial Estate,",
        "Haridwar, Uttarakhand - 249401",
        "Consumer Care Helpline: 1800-222-3333",
        "Email: support@naturaherbals.com",
        "Country of Origin: Made in India"
        # NOTE: MRP intentionally omitted!
    ]
    y = 180
    for line in lines_p2:
        d2.text((70, y), line, fill=(15, 23, 42))
        y += 34

    p2_path = os.path.join(SAMPLE_DIR, "sample_2_missing_mrp.jpg")
    img2.save(p2_path, quality=95)
    samples.append({
        "id": "sample_2",
        "name": "Ayurvedic Cream (Expected: FAIL - Missing MRP)",
        "path": p2_path,
        "filename": "sample_2_missing_mrp.jpg",
        "expected_verdict": "FAIL",
        "description": "Rule 6(1)(e) Violation: Package completely omits Maximum Retail Price (MRP).",
        "default_selling_price": 120.0
    })

    # -------------------------------------------------------------
    # 3. Non-Standard Unit Flour (FAIL)
    # -------------------------------------------------------------
    img3 = Image.new("RGB", (800, 600), color=(253, 248, 238))
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([(20, 20), (780, 580)], outline=(180, 110, 30), width=3)
    d3.text((50, 50), "GOLDEN HARVEST", fill=(180, 110, 30))
    d3.text((50, 90), "PREMIUM SHARBATI WHEAT FLOUR", fill=(20, 20, 20))
    d3.line([(50, 135), (750, 135)], fill=(210, 150, 70), width=2)

    d3.rectangle([(50, 155), (750, 545)], fill=(255, 255, 255), outline=(220, 215, 200), width=1)
    lines_p3 = [
        "PACKAGING & COMMODITY DECLARATIONS:",
        "",
        "Generic Name: Whole Wheat Atta",
        "Net Weight: 5 gms",  # Violation: uses prohibited 'gms' instead of standard 'g'
        "MRP: Rs. 280.00 (Inclusive of all taxes)",
        "Packed on: 07/2026",
        "Manufactured and Marketed by:",
        "Golden Grain Agro Mills Ltd, G.T. Road, Karnal, Haryana - 132001",
        "Consumer Care: care@goldengrain.in | Tel: 0184-225588",
        "Country of Origin: Made in India"
    ]
    y = 180
    for line in lines_p3:
        d3.text((70, y), line, fill=(15, 23, 42))
        y += 34

    p3_path = os.path.join(SAMPLE_DIR, "sample_3_nonstandard_unit.jpg")
    img3.save(p3_path, quality=95)
    samples.append({
        "id": "sample_3",
        "name": "Wheat Flour (Expected: FAIL - Prohibited Unit 'gms')",
        "path": p3_path,
        "filename": "sample_3_nonstandard_unit.jpg",
        "expected_verdict": "FAIL",
        "description": "Rule 6(1)(b) & Rule 13 Violation: Package uses illegal non-standard unit symbol 'gms' instead of mandatory metric symbol 'g'.",
        "default_selling_price": 280.0
    })

    # -------------------------------------------------------------
    # 4. Blurry Detergent (REVIEW)
    # -------------------------------------------------------------
    img4 = Image.new("RGB", (800, 600), color=(235, 240, 250))
    d4 = ImageDraw.Draw(img4)
    d4.rectangle([(20, 20), (780, 580)], outline=(30, 60, 140), width=3)
    d4.text((50, 50), "ULTRA CLEAN", fill=(30, 60, 140))
    d4.text((50, 90), "SURF DETERGENT POWDER", fill=(20, 20, 20))
    
    # Intentionally low contrast / faint text
    lines_p4 = [
        "Generic: Detergent Powder",
        "Net Wt: 1 kg",
        "MRP: Rs. 95 (Incl. Taxes)",
        "Mfg: 05/2026",
        "Mfg by: Washwell Chemicals, Vapi"
    ]
    y = 180
    for line in lines_p4:
        d4.text((70, y), line, fill=(190, 195, 205)) # Low contrast
        y += 40

    # Apply heavy Gaussian blur to trigger low blur variance & OCR uncertainty
    blurred = img4.filter(ImageFilter.GaussianBlur(radius=5.5))
    p4_path = os.path.join(SAMPLE_DIR, "sample_4_blurry_detergent.jpg")
    blurred.save(p4_path, quality=60)
    samples.append({
        "id": "sample_4",
        "name": "Detergent Pouch (Expected: REVIEW - Blurred Image)",
        "path": p4_path,
        "filename": "sample_4_blurry_detergent.jpg",
        "expected_verdict": "REVIEW",
        "description": "System detects severe image blur and low contrast. In accordance with Section 7, flags for human inspector review rather than making an unverified legal determination.",
        "default_selling_price": 95.0
    })

    # -------------------------------------------------------------
    # 5. Overpriced Edible Oil (MRP ₹140, Shop Price ₹180 -> FAIL)
    # -------------------------------------------------------------
    img5 = Image.new("RGB", (800, 600), color=(255, 252, 235))
    d5 = ImageDraw.Draw(img5)
    d5.rectangle([(20, 20), (780, 580)], outline=(190, 140, 0), width=3)
    d5.text((50, 45), "SUNPURE AGRO", fill=(190, 140, 0))
    d5.text((50, 85), "REFINED SUNFLOWER OIL", fill=(20, 20, 20))
    d5.line([(50, 130), (750, 130)], fill=(220, 180, 50), width=2)

    d5.rectangle([(50, 150), (750, 550)], fill=(255, 255, 255), outline=(220, 200, 150), width=1)
    lines_p5 = [
        "STATUTORY PACKAGING DECLARATIONS:",
        "",
        "Generic Name: Edible Refined Sunflower Oil",
        "Net Volume: 1 L",
        "MRP: Rs. 140.00 (Inclusive of all taxes)",
        "Date of Packing: 08/2026",
        "Manufactured and Packed by:",
        "Pure Agri Oils Ltd, Plot 19, MIDC, Pune, Maharashtra - 411018",
        "Consumer Helpline: 020-25667788 | care@pureagrioils.com",
        "Country of Origin: Made in India"
    ]
    y = 170
    for line in lines_p5:
        d5.text((70, y), line, fill=(15, 23, 42))
        y += 32

    p5_path = os.path.join(SAMPLE_DIR, "sample_5_overpriced_oil.jpg")
    img5.save(p5_path, quality=95)
    samples.append({
        "id": "sample_5",
        "name": "Sunflower Oil (Expected: FAIL - Overpricing ₹180 vs ₹140 MRP)",
        "path": p5_path,
        "filename": "sample_5_overpriced_oil.jpg",
        "expected_verdict": "FAIL",
        "description": "Package has printed MRP of ₹140. When inspector enters actual shop selling price of ₹180, Section 36(1) of Legal Metrology Act flags illegal overcharging.",
        "default_selling_price": 180.0
    })

    return samples
