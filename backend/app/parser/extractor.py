import re
from typing import Dict, Any, List

class DeclarationExtractor:
    def __init__(self):
        # Regex patterns for Legal Metrology mandatory declarations
        self.mrp_patterns = [
            # e.g. "MRP: ₹ 50.00 (Incl. of all taxes)" or "M.R.P. Rs. 50" or "MRP Rs 50/-"
            re.compile(r'(?:M\.?R\.?P\.?|MAX(?:IMUM)?\s*RETAIL\s*PRICE)[^\d₹Rs]*[₹\sRs\.]*\s*([0-9]+(?:\.[0-9]{1,2})?)', re.IGNORECASE),
            re.compile(r'[₹Rs\.]+\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:\/|\-|\s)*(?:INCL|INCLUSIVE)', re.IGNORECASE),
            re.compile(r'MRP\s*[:\-\=]?\s*([0-9]+(?:\.[0-9]{1,2})?)', re.IGNORECASE)
        ]

        self.tax_inclusion_pattern = re.compile(
            r'(?:INCL|INCLUSIVE)\s*(?:OF)?\s*(?:ALL)?\s*TAX(?:ES)?',
            re.IGNORECASE
        )

        self.net_qty_patterns = [
            # e.g. "Net Qty: 500 g" or "Net Wt: 1 kg" or "Net Quantity: 500 ml" or "Net Contents: 1 L"
            re.compile(r'(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT|CONTENTS?|VOL|VOLUME))\s*[:\-\=]?\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)', re.IGNORECASE),
            re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gm|gms|ml|l|ltr|litres?|grams?|kilos?)\b', re.IGNORECASE)
        ]

        self.date_patterns = [
            # e.g. "Mfg: 08/2026" or "Pkd on: Aug 2026" or "Packed: 10/08/2026" or "Date of Mfg: 08/26"
            re.compile(r'(?:MFD|MFG|PACKED|PKD|DOM|DATE\s*OF\s*(?:MFG|PACKING))\s*[:\-\=]?\s*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4}|[0-9]{1,2}[\/\-\.][0-9]{2,4}|(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*[\s\.\,\-\/]+[0-9]{2,4})', re.IGNORECASE),
            re.compile(r'\b(0[1-9]|1[0-2])[\/\-\.](202[0-9]|203[0-9]|[2-3][0-9])\b'),
            re.compile(r'\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*[\s\.\,\-]+(202[0-9]|203[0-9]|[2-3][0-9])\b', re.IGNORECASE)
        ]

        self.mfg_patterns = [
            # e.g. "Mfg by:", "Manufactured by:", "Packed by:", "Marketed by:"
            re.compile(r'(?:MFD|MANUFACTURED|PACKED|PKD|PRODUCED|MARKETED|MKTD|IMPORTED)\s*(?:AND\s*PACKED)?\s*BY\s*[:\-\=]?\s*(.+)', re.IGNORECASE),
            re.compile(r'(?:MFG\s*BY|NAME\s*&\s*ADDRESS\s*OF\s*MFR)\s*[:\-\=]?\s*(.+)', re.IGNORECASE)
        ]

        self.consumer_care_patterns = [
            # e.g. "Consumer Care:", "Customer Support:", "Toll Free:", "Email: care@..."
            re.compile(r'(?:CONSUMER\s*CARE|CUSTOMER\s*CARE|CUSTOMER\s*SUPPORT|HELPLINE|TOLL\s*FREE|FEEDBACK|COMPLAINTS?)\s*[:\-\=]?\s*(.+)', re.IGNORECASE),
            re.compile(r'(?:EMAIL|E-MAIL)\s*[:\-\=]?\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', re.IGNORECASE),
            re.compile(r'(?:TEL|PHONE|CALL|TOLL[\s\-]FREE)\s*[:\-\=]?\s*([0-9]{3,5}[\s\-]?[0-9]{3,7}|1800[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4})', re.IGNORECASE)
        ]

        self.origin_patterns = [
            re.compile(r'(?:COUNTRY\s*OF\s*ORIGIN|MADE\s*IN)\s*[:\-\=]?\s*([a-zA-Z\s]+)', re.IGNORECASE)
        ]

        self.usp_patterns = [
            # e.g. "USP: Rs. 0.10 / g" or "Unit Sale Price: ₹ 0.50 / ml"
            re.compile(r'(?:USP|UNIT\s*SALE\s*PRICE)\s*[:\-\=]?\s*[₹Rs\.]*\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:\/|\s*per\s*)([a-zA-Z]+)', re.IGNORECASE)
        ]

    def extract_declarations(self, ocr_data: dict) -> dict:
        lines = ocr_data.get("lines", [])
        full_text = ocr_data.get("full_text", "")
        detections_to_draw = []

        # Default empty declaration structure
        declarations = {
            "product_name": {"value": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
            "mrp": {"value": None, "raw": None, "currency": "₹", "inclusive_of_taxes": False, "confidence": 0.0, "box": None, "status": "MISSING"},
            "net_quantity": {"value": None, "unit": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
            "mfg_date": {"value": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
            "manufacturer": {"value": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
            "consumer_care": {"value": None, "contact": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
            "country_of_origin": {"value": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
            "unit_sale_price": {"value": None, "unit": None, "raw": None, "confidence": 0.0, "box": None, "status": "MISSING"},
        }

        # 1. Look for MRP
        for line in lines:
            text = line["text"]
            for pat in self.mrp_patterns:
                m = pat.search(text)
                if m and declarations["mrp"]["status"] == "MISSING":
                    try:
                        val = float(m.group(1))
                        # Check taxes in this line or nearby
                        has_taxes = bool(self.tax_inclusion_pattern.search(text) or self.tax_inclusion_pattern.search(full_text))
                        declarations["mrp"] = {
                            "value": val,
                            "raw": text,
                            "currency": "₹",
                            "inclusive_of_taxes": has_taxes,
                            "confidence": line["confidence"],
                            "box": line["box"],
                            "status": "PRESENT"
                        }
                        detections_to_draw.append({
                            "box": line["box"],
                            "label": f"MRP: Rs. {val}",
                            "field_type": "mrp"
                        })
                        break
                    except (ValueError, IndexError):
                        continue

        # 2. Look for Net Quantity
        for line in lines:
            text = line["text"]
            for pat in self.net_qty_patterns:
                m = pat.search(text)
                if m and declarations["net_quantity"]["status"] == "MISSING":
                    try:
                        val = float(m.group(1))
                        unit = m.group(2).lower()
                        declarations["net_quantity"] = {
                            "value": val,
                            "unit": unit,
                            "raw": text,
                            "confidence": line["confidence"],
                            "box": line["box"],
                            "status": "PRESENT"
                        }
                        detections_to_draw.append({
                            "box": line["box"],
                            "label": f"Net Qty: {val} {unit}",
                            "field_type": "net_quantity"
                        })
                        break
                    except (ValueError, IndexError):
                        continue

        # 3. Look for Date of Mfg / Packing
        for line in lines:
            text = line["text"]
            for pat in self.date_patterns:
                m = pat.search(text)
                if m and declarations["mfg_date"]["status"] == "MISSING":
                    date_val = m.group(1) if m.groups() else m.group(0)
                    declarations["mfg_date"] = {
                        "value": date_val.strip(),
                        "raw": text,
                        "confidence": line["confidence"],
                        "box": line["box"],
                        "status": "PRESENT"
                    }
                    detections_to_draw.append({
                        "box": line["box"],
                        "label": f"Date: {date_val.strip()}",
                        "field_type": "mfg_date"
                    })
                    break

        # 4. Look for Manufacturer / Packer
        for i, line in enumerate(lines):
            text = line["text"]
            for pat in self.mfg_patterns:
                m = pat.search(text)
                if m and declarations["manufacturer"]["status"] == "MISSING":
                    mfg_name = m.group(1).strip()
                    # If line is short, concatenate next line (often the street address)
                    if len(mfg_name) < 20 and i + 1 < len(lines):
                        mfg_name += ", " + lines[i+1]["text"].strip()
                    declarations["manufacturer"] = {
                        "value": mfg_name,
                        "raw": text,
                        "confidence": line["confidence"],
                        "box": line["box"],
                        "status": "PRESENT"
                    }
                    detections_to_draw.append({
                        "box": line["box"],
                        "label": "Manufacturer Details",
                        "field_type": "manufacturer"
                    })
                    break

        # 5. Look for Consumer Care details
        for line in lines:
            text = line["text"]
            for pat in self.consumer_care_patterns:
                m = pat.search(text)
                if m and declarations["consumer_care"]["status"] == "MISSING":
                    val = m.group(1).strip()
                    declarations["consumer_care"] = {
                        "value": val,
                        "contact": val,
                        "raw": text,
                        "confidence": line["confidence"],
                        "box": line["box"],
                        "status": "PRESENT"
                    }
                    detections_to_draw.append({
                        "box": line["box"],
                        "label": "Consumer Care Cell",
                        "field_type": "consumer_care"
                    })
                    break

        # 6. Look for Country of Origin
        for line in lines:
            text = line["text"]
            for pat in self.origin_patterns:
                m = pat.search(text)
                if m and declarations["country_of_origin"]["status"] == "MISSING":
                    origin = m.group(1).strip()
                    declarations["country_of_origin"] = {
                        "value": origin,
                        "raw": text,
                        "confidence": line["confidence"],
                        "box": line["box"],
                        "status": "PRESENT"
                    }
                    break
        if declarations["country_of_origin"]["status"] == "MISSING" and "made in india" in full_text.lower():
            declarations["country_of_origin"] = {
                "value": "India",
                "raw": "Made in India",
                "confidence": 0.90,
                "box": None,
                "status": "PRESENT"
            }

        # 7. Look for Unit Sale Price (USP)
        for line in lines:
            text = line["text"]
            for pat in self.usp_patterns:
                m = pat.search(text)
                if m and declarations["unit_sale_price"]["status"] == "MISSING":
                    declarations["unit_sale_price"] = {
                        "value": float(m.group(1)),
                        "unit": m.group(2).lower(),
                        "raw": text,
                        "confidence": line["confidence"],
                        "box": line["box"],
                        "status": "PRESENT"
                    }
                    break

        # 8. Product Name / Commodity Generic Title
        # Often the most prominent line near the top with highest character size or first non-legal line
        if lines:
            # Check lines that don't match legal phrases
            candidate = None
            candidate_box = None
            candidate_conf = 0.0
            for line in lines[:5]:
                t = line["text"].strip()
                if len(t) > 3 and not any(kw in t.lower() for kw in ["mrp", "net", "mfg", "pkd", "rs", "batch", "care"]):
                    candidate = t
                    candidate_box = line["box"]
                    candidate_conf = line["confidence"]
                    break
            if candidate:
                declarations["product_name"] = {
                    "value": candidate,
                    "raw": candidate,
                    "confidence": candidate_conf,
                    "box": candidate_box,
                    "status": "PRESENT"
                }
                detections_to_draw.append({
                    "box": candidate_box,
                    "label": f"Commodity: {candidate}",
                    "field_type": "product_name"
                })

        return {
            "declarations": declarations,
            "annotations_to_draw": detections_to_draw
        }
