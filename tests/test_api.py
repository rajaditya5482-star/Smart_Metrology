import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_suite():
    print("--- 1. Testing Health Endpoint ---")
    res = client.get("/api/health")
    assert res.status_code == 200
    print("Health check OK:", res.json()["status"])

    print("\n--- 2. Testing Sample Packages Listing ---")
    res = client.get("/api/samples")
    assert res.status_code == 200
    samples = res.json()
    assert len(samples) >= 5
    print(f"Sample packages loaded: {len(samples)}")
    for s in samples:
        print(f"  - {s['name']} (Expected: {s['expected_verdict']})")

    print("\n--- 3. Testing Inspection on Compliant Sample ---")
    res = client.post(
        "/api/inspect",
        data={
            "sample_filename": "sample_1_compliant_biscuits.jpg",
            "shop_name": "Royal Mart",
            "shop_location": "Karol Bagh, New Delhi",
            "selling_price": "50.0",
            "inspector_id": "INSP-TEST-001"
        }
    )
    assert res.status_code == 200
    data = res.json()
    record_id = data["id"]
    print("Inspection ID:", data["inspection_id"])
    print("Verdict:", data["verdict"])
    print("Blockchain Block Index:", data["blockchain"]["block_index"])
    print("Record SHA-256:", data["blockchain"]["record_sha256"])
    assert data["verdict"] == "PASS", f"Expected PASS, got {data['verdict']}"

    print("\n--- 4. Testing Inspection on Missing MRP Sample (Rule 6(1)(e)) ---")
    res2 = client.post(
        "/api/inspect",
        data={
            "sample_filename": "sample_2_missing_mrp.jpg",
            "shop_name": "Beauty Store",
            "shop_location": "Haridwar",
            "inspector_id": "INSP-TEST-001"
        }
    )
    assert res2.status_code == 200
    data2 = res2.json()
    print("Sample 2 Verdict:", data2["verdict"])
    print("Violations:", [v["title"] for v in data2["violations"]])
    assert data2["verdict"] == "FAIL", f"Expected FAIL, got {data2['verdict']}"
    assert any("MRP" in v["title"] for v in data2["violations"])

    print("\n--- 5. Testing Overpricing Check (Sec 36(1): Selling Price > MRP) ---")
    res5 = client.post(
        "/api/inspect",
        data={
            "sample_filename": "sample_5_overpriced_oil.jpg",
            "shop_name": "General Provision",
            "shop_location": "Pune",
            "selling_price": "180.0", # Printed MRP is 140
            "inspector_id": "INSP-TEST-001"
        }
    )
    assert res5.status_code == 200
    data5 = res5.json()
    print("Sample 5 Verdict:", data5["verdict"])
    print("Violations:", [v["title"] for v in data5["violations"]])
    assert data5["verdict"] == "FAIL", f"Expected FAIL, got {data5['verdict']}"
    assert any("Overpricing" in v["title"] for v in data5["violations"])

    print("\n--- 6. Testing Blockchain Tamper-Evidence & Integrity ---")
    # Verify untampered
    res_verify = client.post(f"/api/records/{record_id}/verify-tamper")
    assert res_verify.status_code == 200
    v1 = res_verify.json()
    print("Untampered check: is_valid =", v1["is_valid"], "(Status:", v1["status"], ")")
    assert v1["is_valid"] is True

    # Simulate tampering (alters DB value directly without blockchain)
    print("Simulating database record alteration (e.g. changing MRP)...")
    res_tamper = client.post(f"/api/records/{record_id}/simulate-tamper?fake_mrp=35.0")
    assert res_tamper.status_code == 200
    v2 = res_tamper.json()
    print("Tampered check: is_valid =", v2["is_valid"], "(Status:", v2["status"], ")")
    print("  Recorded Blockchain Hash:", v2["recorded_blockchain_data_hash"])
    print("  Recalculated DB Hash:    ", v2["current_recalculated_hash"])
    assert v2["is_valid"] is False, "Blockchain hash comparison should detect tampering!"

    # Revert tampering
    print("Reverting database alteration...")
    res_revert = client.post(f"/api/records/{record_id}/revert-tamper")
    assert res_revert.status_code == 200
    v3 = res_revert.json()
    print("Restored check: is_valid =", v3["is_valid"], "(Status:", v3["status"], ")")
    assert v3["is_valid"] is True

    print("\n--- 7. Testing Counterfeit Serial ID Verification & Clone Detection ---")
    # First scan at Shop 1
    res_scan1 = client.post(
        "/api/counterfeit/verify",
        data={"serial_id": "ABC001", "shop_name": "Store A - Delhi"}
    )
    assert res_scan1.status_code == 200
    s1 = res_scan1.json()
    print("Scan 1 at Store A: Verdict =", s1["verdict"], "(Genuine =", s1["is_genuine"], ")")
    assert s1["verdict"] == "VERIFIED_AUTHENTIC"

    # Second scan at Shop 2 (Duplicate clone alert!)
    res_scan2 = client.post(
        "/api/counterfeit/verify",
        data={"serial_id": "ABC001", "shop_name": "Store B - Mumbai"}
    )
    assert res_scan2.status_code == 200
    s2 = res_scan2.json()
    print("Scan 2 at Store B: Verdict =", s2["verdict"], "(Title =", s2.get("title"), ")")
    assert s2["verdict"] == "DUPLICATE_SUSPICIOUS"

    print("\n--- 8. Testing Official PDF Inspection Certificate Download ---")
    res_pdf = client.get(f"/api/reports/{record_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content[:4] == b"%PDF"
    print("PDF generated and verified successfully! Size:", len(res_pdf.content), "bytes")

    print("\n--- 9. Testing Analytics Dashboard Stats ---")
    res_stats = client.get("/api/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    print(f"Total Inspections: {stats['total_inspections']}, Passed: {stats['passed']}, Failed: {stats['failed']}, Blocks: {stats['blocks_mined']}")

    print("\n=======================================================")
    print("ALL API END-TO-END TESTS PASSED WITH 100% SUCCESS!")
    print("=======================================================")

if __name__ == "__main__":
    test_api_suite()
