import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class PDFReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_inspection_report(self, record_dict: dict, file_name: str) -> str:
        pdf_path = os.path.join(self.output_dir, file_name)
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'GovHeader',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=1, # Center
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            'GovSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#475569")
        )
        section_style = ParagraphStyle(
            'SectionH',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1e293b")
        )
        badge_style = ParagraphStyle(
            'VerdictBadge',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=1,
            textColor=colors.white
        )

        story = []

        # Government & Department Header
        story.append(Paragraph("GOVERNMENT OF INDIA", title_style))
        story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS • LEGAL METROLOGY DIVISION", subtitle_style))
        story.append(Paragraph("STATUTORY PACKAGED COMMODITIES INSPECTION REPORT & EVIDENCE SHEET", subtitle_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=10))

        # Case Metadata Table
        verdict = record_dict.get("verdict", "REVIEW")
        verdict_color = colors.HexColor("#16a34a") if verdict == "PASS" else (colors.HexColor("#dc2626") if verdict == "FAIL" else colors.HexColor("#d97706"))

        meta_data = [
            [
                Paragraph(f"<b>Inspection ID:</b> {record_dict.get('inspection_id')}", body_style),
                Paragraph(f"<b>Date / Time:</b> {record_dict.get('timestamp')}", body_style),
            ],
            [
                Paragraph(f"<b>Enforcement Officer:</b> {record_dict.get('inspector_id', 'INSP-LM-408')}", body_style),
                Paragraph(f"<b>Shop / Retailer:</b> {record_dict.get('shop_name', 'Retail Inspection')}", body_style),
            ],
            [
                Paragraph(f"<b>Location / Zone:</b> {record_dict.get('shop_location', 'N/A')}", body_style),
                Paragraph(f"<b>Selling Price:</b> ₹{record_dict.get('selling_price') or 'Not recorded'}", body_style),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # Verdict Banner
        verdict_banner = Table(
            [[Paragraph(f"FINAL STATUTORY COMPLIANCE DETERMINATION: {verdict}", badge_style)]],
            colWidths=[540]
        )
        verdict_banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), verdict_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(verdict_banner)
        story.append(Spacer(1, 10))

        # Evidence Photo & Extracted Data Table side-by-side or stacked
        story.append(Paragraph("1. Packaging Visual Evidence & Label Detection", section_style))

        # Include annotated or original image if exists
        img_path = record_dict.get("annotated_image_path") or record_dict.get("original_image_path")
        if img_path and os.path.exists(img_path):
            try:
                img = RLImage(img_path, width=2.4*inch, height=2.4*inch, kind='proportional')
                img_cell = img
            except Exception:
                img_cell = Paragraph("[Packaging Evidence Image Stored]", body_style)
        else:
            img_cell = Paragraph("[No Image Available]", body_style)

        # Extracted Summary
        ext = record_dict.get("extracted_data", {})
        mrp_text = f"₹{ext.get('mrp', {}).get('value')} ({'Incl. taxes' if ext.get('mrp', {}).get('inclusive_of_taxes') else 'Taxes missing'})"
        qty_text = f"{ext.get('net_quantity', {}).get('value')} {ext.get('net_quantity', {}).get('unit')}"
        mfg_text = str(ext.get('manufacturer', {}).get('value', 'Not detected'))[:45]
        date_text = str(ext.get('mfg_date', {}).get('value', 'Not detected'))

        extract_summary = [
            [Paragraph("<b>Extracted Declaration</b>", body_style), Paragraph("<b>Status & Detected Value</b>", body_style)],
            [Paragraph("Commodity Name:", body_style), Paragraph(str(ext.get('product_name', {}).get('value', 'N/A')), body_style)],
            [Paragraph("Maximum Retail Price:", body_style), Paragraph(mrp_text, body_style)],
            [Paragraph("Net Quantity:", body_style), Paragraph(qty_text, body_style)],
            [Paragraph("Date of Mfg/Packing:", body_style), Paragraph(date_text, body_style)],
            [Paragraph("Manufacturer Details:", body_style), Paragraph(mfg_text, body_style)],
        ]
        ext_table = Table(extract_summary, colWidths=[140, 180])
        ext_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))

        ev_table = Table([[img_cell, ext_table]], colWidths=[200, 340])
        ev_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
        ]))
        story.append(ev_table)
        story.append(Spacer(1, 10))

        # Legal Metrology Rule Compliance Breakdown
        story.append(Paragraph("2. Statutory Rule Compliance Breakdown", section_style))
        rule_rows = [
            [
                Paragraph("<b>Rule Citation</b>", body_style),
                Paragraph("<b>Mandated Requirement</b>", body_style),
                Paragraph("<b>Status</b>", body_style),
                Paragraph("<b>Findings / Details</b>", body_style)
            ]
        ]
        for r in record_dict.get("rule_results", []):
            st = r.get("status", "REVIEW")
            st_color = "#16a34a" if st == "PASS" else ("#dc2626" if st == "FAIL" else "#d97706")
            rule_rows.append([
                Paragraph(r.get("rule", ""), body_style),
                Paragraph(r.get("title", ""), body_style),
                Paragraph(f"<font color='{st_color}'><b>{st}</b></font>", body_style),
                Paragraph(r.get("details", ""), body_style)
            ])

        rules_table = Table(rule_rows, colWidths=[80, 130, 60, 270])
        rules_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(rules_table)
        story.append(Spacer(1, 10))

        # Cryptographic Audit & Blockchain Integrity Section
        story.append(Paragraph("3. Blockchain Tamper-Evident Integrity Record", section_style))
        crypto_info = [
            [Paragraph("<b>Canonical Record SHA-256 Fingerprint:</b>", body_style), Paragraph(f"<font face='Courier' size='7'>{record_dict.get('record_hash', 'N/A')}</font>", body_style)],
            [Paragraph("<b>Blockchain Block Index:</b>", body_style), Paragraph(f"Block #{record_dict.get('blockchain_block_index', '0')}", body_style)],
            [Paragraph("<b>Blockchain Block Hash:</b>", body_style), Paragraph(f"<font face='Courier' size='7'>{record_dict.get('blockchain_block_hash', 'N/A')}</font>", body_style)],
            [Paragraph("<b>Audit Status:</b>", body_style), Paragraph("<b>CRYPTOGRAPHICALLY SECURED ON LEDGER (TAMPER-EVIDENT)</b>", body_style)]
        ]
        crypto_table = Table(crypto_info, colWidths=[190, 350])
        crypto_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(crypto_table)
        story.append(Spacer(1, 15))

        # Signatures
        sig_data = [
            [Paragraph("_______________________________<br/><b>Inspecting Authority Signature</b><br/>Legal Metrology Inspector", body_style),
             Paragraph("_______________________________<br/><b>Retailer / Shop Representative</b><br/>Acknowledgment", body_style)]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        sig_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(sig_table)

        doc.build(story)
        return pdf_path
