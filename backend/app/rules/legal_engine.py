from typing import Dict, Any, List

class LegalMetrologyRuleEngine:
    """
    Compliance Decision Engine based on:
    - The Legal Metrology Act, 2009
    - The Legal Metrology (Packaged Commodities) Rules, 2011 (as amended)
    """

    # Permissible metric units under Rule 13 and Second Schedule
    STANDARD_MASS_UNITS = {"g", "kg", "mg"}
    STANDARD_VOLUME_UNITS = {"ml", "l"}
    STANDARD_LENGTH_UNITS = {"m", "cm", "mm"}
    STANDARD_NUMBER_UNITS = {"n", "u"}

    NON_STANDARD_UNITS_MAP = {
        "gm": "g",
        "gms": "g",
        "kilo": "kg",
        "kilos": "kg",
        "ltr": "l",
        "ltrs": "l",
        "litre": "l",
        "litres": "l"
    }

    CONFIDENCE_THRESHOLD_REVIEW = 0.55

    def evaluate(self, declarations: dict, ocr_metadata: dict, cv_metadata: dict, selling_price: float = None) -> dict:
        results = []
        violations = []
        review_reasons = []

        is_blurry = cv_metadata.get("is_blurry", False)
        mean_ocr_conf = ocr_metadata.get("mean_confidence", 0.0)

        # -------------------------------------------------------------
        # 1. Rule 6(1)(e) - Maximum Retail Price (MRP) & Tax Inclusivity
        # -------------------------------------------------------------
        mrp_data = declarations.get("mrp", {})
        if mrp_data.get("status") == "PRESENT" and mrp_data.get("value") is not None:
            mrp_val = mrp_data["value"]
            mrp_conf = mrp_data.get("confidence", 1.0)

            if mrp_conf < self.CONFIDENCE_THRESHOLD_REVIEW:
                review_reasons.append({
                    "rule": "Rule 6(1)(e)",
                    "title": "MRP OCR Uncertainty",
                    "description": f"MRP was detected as Rs. {mrp_val} but OCR confidence is low ({int(mrp_conf*100)}%). Verification recommended."
                })
                results.append({
                    "rule": "Rule 6(1)(e)",
                    "title": "Maximum Retail Price (MRP)",
                    "status": "REVIEW",
                    "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(e)",
                    "details": f"Declared: ₹{mrp_val}. Low visual certainty requires inspector confirmation."
                })
            else:
                # Check tax inclusion phrase
                if not mrp_data.get("inclusive_of_taxes", False):
                    violations.append({
                        "rule": "Rule 6(1)(e)",
                        "title": "Taxes Not Specified on MRP",
                        "description": "Rule 6(1)(e) mandates the words 'inclusive of all taxes' or 'incl. of all taxes' with the retail sale price."
                    })
                    results.append({
                        "rule": "Rule 6(1)(e)",
                        "title": "Maximum Retail Price (MRP)",
                        "status": "FAIL",
                        "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(e)",
                        "details": f"Declared: ₹{mrp_val} but missing mandatory 'incl. of all taxes' declaration."
                    })
                else:
                    results.append({
                        "rule": "Rule 6(1)(e)",
                        "title": "Maximum Retail Price (MRP)",
                        "status": "PASS",
                        "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(e)",
                        "details": f"Compliant: ₹{mrp_val} (Inclusive of all taxes)."
                    })
        else:
            violations.append({
                "rule": "Rule 6(1)(e)",
                "title": "Missing MRP Declaration",
                "description": "Package fails to display Maximum Retail Price (MRP) in Indian currency."
            })
            results.append({
                "rule": "Rule 6(1)(e)",
                "title": "Maximum Retail Price (MRP)",
                "status": "FAIL",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(e)",
                "details": "Definite Violation: MRP is missing or completely unreadable."
            })

        # -------------------------------------------------------------
        # 2. Rule 6(1)(b) - Net Quantity & Metric System Standard Units
        # -------------------------------------------------------------
        net_qty = declarations.get("net_quantity", {})
        if net_qty.get("status") == "PRESENT" and net_qty.get("value") is not None:
            unit = str(net_qty.get("unit", "")).lower()
            val = net_qty.get("value")
            qty_conf = net_qty.get("confidence", 1.0)

            all_standard = self.STANDARD_MASS_UNITS | self.STANDARD_VOLUME_UNITS | self.STANDARD_LENGTH_UNITS | self.STANDARD_NUMBER_UNITS

            if unit in self.NON_STANDARD_UNITS_MAP:
                correct = self.NON_STANDARD_UNITS_MAP[unit]
                violations.append({
                    "rule": "Rule 6(1)(b) & Rule 13",
                    "title": "Non-Standard Unit of Measurement",
                    "description": f"Used '{unit}' instead of mandatory statutory unit '{correct}'. Rule 13 strictly prohibits symbols like 'gms' or 'kilos'."
                })
                results.append({
                    "rule": "Rule 6(1)(b)",
                    "title": "Net Quantity & Metric Units",
                    "status": "FAIL",
                    "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(b) & Rule 13",
                    "details": f"Violation: Non-standard unit '{unit}' used. Standard symbol required: '{correct}'."
                })
            elif unit in all_standard:
                if qty_conf < self.CONFIDENCE_THRESHOLD_REVIEW:
                    review_reasons.append({
                        "rule": "Rule 6(1)(b)",
                        "title": "Net Quantity OCR Uncertainty",
                        "description": f"Net quantity read as {val} {unit} with low confidence ({int(qty_conf*100)}%)."
                    })
                    results.append({
                        "rule": "Rule 6(1)(b)",
                        "title": "Net Quantity & Metric Units",
                        "status": "REVIEW",
                        "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(b)",
                        "details": f"Declared: {val} {unit}. Requires inspector verification."
                    })
                else:
                    results.append({
                        "rule": "Rule 6(1)(b)",
                        "title": "Net Quantity & Metric Units",
                        "status": "PASS",
                        "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(b)",
                        "details": f"Compliant: {val} {unit} using standard metric unit."
                    })
            else:
                review_reasons.append({
                    "rule": "Rule 6(1)(b)",
                    "title": "Unrecognized Unit Symbol",
                    "description": f"Detected net quantity value '{val}' with unrecognized unit symbol '{unit}'."
                })
                results.append({
                    "rule": "Rule 6(1)(b)",
                    "title": "Net Quantity & Metric Units",
                    "status": "REVIEW",
                    "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(b)",
                    "details": f"Unrecognized unit '{unit}'. Requires manual review."
                })
        else:
            violations.append({
                "rule": "Rule 6(1)(b)",
                "title": "Missing Net Quantity Declaration",
                "description": "Package fails to declare net quantity of commodity in standard units of weight or measure."
            })
            results.append({
                "rule": "Rule 6(1)(b)",
                "title": "Net Quantity & Metric Units",
                "status": "FAIL",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(b)",
                "details": "Definite Violation: Net Quantity declaration is absent."
            })

        # -------------------------------------------------------------
        # 3. Rule 6(1)(c) - Manufacturer / Packer / Importer Details
        # -------------------------------------------------------------
        mfg = declarations.get("manufacturer", {})
        if mfg.get("status") == "PRESENT" and mfg.get("value"):
            results.append({
                "rule": "Rule 6(1)(c)",
                "title": "Manufacturer / Packer Information",
                "status": "PASS",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(c)",
                "details": f"Compliant: '{mfg['value'][:70]}...'"
            })
        else:
            violations.append({
                "rule": "Rule 6(1)(c)",
                "title": "Missing Manufacturer / Packer Identity",
                "description": "Name and complete address of the manufacturer or packer or importer is not declared on the package."
            })
            results.append({
                "rule": "Rule 6(1)(c)",
                "title": "Manufacturer / Packer Information",
                "status": "FAIL",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(c)",
                "details": "Definite Violation: Manufacturer/Packer information missing."
            })

        # -------------------------------------------------------------
        # 4. Rule 6(1)(d) - Date of Manufacture / Packing
        # -------------------------------------------------------------
        mfg_date = declarations.get("mfg_date", {})
        if mfg_date.get("status") == "PRESENT" and mfg_date.get("value"):
            results.append({
                "rule": "Rule 6(1)(d)",
                "title": "Date of Manufacture / Pre-packing",
                "status": "PASS",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(d)",
                "details": f"Compliant: Declared as {mfg_date['value']}."
            })
        else:
            violations.append({
                "rule": "Rule 6(1)(d)",
                "title": "Missing Date of Manufacture / Packing",
                "description": "The month and year of manufacture or pre-packing is absent."
            })
            results.append({
                "rule": "Rule 6(1)(d)",
                "title": "Date of Manufacture / Pre-packing",
                "status": "FAIL",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(d)",
                "details": "Definite Violation: Month and year of packing not declared."
            })

        # -------------------------------------------------------------
        # 5. Rule 6(1)(a) - Generic / Common Product Name
        # -------------------------------------------------------------
        prod = declarations.get("product_name", {})
        if prod.get("status") == "PRESENT" and prod.get("value"):
            results.append({
                "rule": "Rule 6(1)(a)",
                "title": "Generic / Common Commodity Name",
                "status": "PASS",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(a)",
                "details": f"Compliant: Identified as '{prod['value']}'."
            })
        else:
            review_reasons.append({
                "rule": "Rule 6(1)(a)",
                "title": "Ambiguous Generic Name",
                "description": "Specific generic name not clearly isolated from brand graphics. Manual verification suggested."
            })
            results.append({
                "rule": "Rule 6(1)(a)",
                "title": "Generic / Common Commodity Name",
                "status": "REVIEW",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(a)",
                "details": "Common generic name could not be definitively isolated from packaging artwork."
            })

        # -------------------------------------------------------------
        # 6. Rule 6(1)(n) - Consumer Grievance / Care Cell
        # -------------------------------------------------------------
        care = declarations.get("consumer_care", {})
        if care.get("status") == "PRESENT" and care.get("value"):
            results.append({
                "rule": "Rule 6(1)(n)",
                "title": "Consumer Care Details",
                "status": "PASS",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(n)",
                "details": f"Compliant: Consumer contact declared ({care['value'][:50]})."
            })
        else:
            review_reasons.append({
                "rule": "Rule 6(1)(n)",
                "title": "Consumer Care Details Unreadable or Missing",
                "description": "Consumer care phone or email contact not detected in current view."
            })
            results.append({
                "rule": "Rule 6(1)(n)",
                "title": "Consumer Care Details",
                "status": "REVIEW",
                "citation": "Legal Metrology (Packaged Commodities) Rules, Rule 6(1)(n)",
                "details": "Consumer care helpline or email not clearly located on visible label."
            })

        # -------------------------------------------------------------
        # 7. Overcharging Check (Actual Selling Price vs Declared MRP)
        # -------------------------------------------------------------
        if selling_price is not None and mrp_data.get("value") is not None:
            declared_mrp = mrp_data["value"]
            if selling_price > declared_mrp:
                diff = round(selling_price - declared_mrp, 2)
                violations.append({
                    "rule": "Section 36(1) of Legal Metrology Act, 2009",
                    "title": "Overpricing / Selling Above MRP",
                    "description": f"Shopkeeper is charging ₹{selling_price}, which exceeds the printed MRP of ₹{declared_mrp} by ₹{diff}."
                })
                results.append({
                    "rule": "Section 36(1)",
                    "title": "Anti-Overcharging Compliance",
                    "status": "FAIL",
                    "citation": "Legal Metrology Act, 2009, Section 36(1)",
                    "details": f"Definite Violation: Actual Price (₹{selling_price}) > Printed MRP (₹{declared_mrp}). Overcharge: ₹{diff}."
                })
            else:
                results.append({
                    "rule": "Section 36(1)",
                    "title": "Anti-Overcharging Compliance",
                    "status": "PASS",
                    "citation": "Legal Metrology Act, 2009, Section 36(1)",
                    "details": f"Compliant: Actual Selling Price (₹{selling_price}) does not exceed MRP (₹{declared_mrp})."
                })

        # -------------------------------------------------------------
        # Final Verdict Determination: PASS / FAIL / REVIEW
        # -------------------------------------------------------------
        # Low image quality / blur / severe OCR degradation triggers REVIEW
        if is_blurry and not violations:
            final_verdict = "REVIEW"
            review_reasons.append({
                "rule": "Visual Clarity Check",
                "title": "Image Blur Detected",
                "description": f"Image blur variance is below legal inspection clarity standard. Human review required."
            })
        elif violations:
            final_verdict = "FAIL"
        elif review_reasons:
            final_verdict = "REVIEW"
        else:
            final_verdict = "PASS"

        return {
            "verdict": final_verdict,
            "rule_results": results,
            "violations": violations,
            "review_reasons": review_reasons,
            "total_rules_checked": len(results),
            "passed_count": sum(1 for r in results if r["status"] == "PASS"),
            "failed_count": sum(1 for r in results if r["status"] == "FAIL"),
            "review_count": sum(1 for r in results if r["status"] == "REVIEW"),
        }
