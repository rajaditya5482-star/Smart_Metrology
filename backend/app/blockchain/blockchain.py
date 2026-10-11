import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from ..database.models import BlockchainBlock, InspectionRecord

def calculate_sha256(data_string: str) -> str:
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def calculate_file_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return "0" * 64

def canonical_record_payload(
    inspection_id: str,
    timestamp: str,
    inspector_id: str,
    shop_name: str,
    image_hash: str,
    mrp: float,
    net_qty: float,
    net_unit: str,
    verdict: str,
    violations_summary: str
) -> dict:
    """Produces normalized canonical payload for cryptographic hashing."""
    return {
        "inspection_id": str(inspection_id).strip(),
        "timestamp": str(timestamp).strip(),
        "inspector_id": str(inspector_id).strip(),
        "shop_name": str(shop_name or "").strip(),
        "image_hash": str(image_hash).strip(),
        "mrp": float(mrp) if mrp is not None else 0.0,
        "net_qty": float(net_qty) if net_qty is not None else 0.0,
        "net_unit": str(net_unit or "").strip().lower(),
        "verdict": str(verdict).strip(),
        "violations": str(violations_summary or "").strip(),
    }

class BlockchainLedger:
    def __init__(self, db: Session):
        self.db = db
        self._ensure_genesis()

    def _ensure_genesis(self):
        count = self.db.query(BlockchainBlock).count()
        if count == 0:
            genesis_payload = {
                "message": "SmartMetrology Genesis Block - Legal Metrology Dept",
                "timestamp": "2026-01-01T00:00:00Z"
            }
            data_hash = calculate_sha256(json.dumps(genesis_payload, sort_keys=True))
            genesis_hash = calculate_sha256(f"0::0::{data_hash}::2026-01-01T00:00:00Z::0")

            genesis_block = BlockchainBlock(
                index=0,
                timestamp="2026-01-01T00:00:00Z",
                previous_hash="0" * 64,
                current_hash=genesis_hash,
                data_hash=data_hash,
                payload=genesis_payload,
                nonce=0
            )
            self.db.add(genesis_block)
            self.db.commit()

    def add_inspection_block(self, inspection_payload: dict) -> BlockchainBlock:
        last_block = self.db.query(BlockchainBlock).order_by(BlockchainBlock.index.desc()).first()
        new_index = last_block.index + 1 if last_block else 0
        prev_hash = last_block.current_hash if last_block else "0" * 64
        timestamp = datetime.utcnow().isoformat()

        # Compute payload hash
        canonical_str = json.dumps(inspection_payload, sort_keys=True)
        data_hash = calculate_sha256(canonical_str)

        # Simple proof of work / block hash
        nonce = 0
        block_content = f"{new_index}::{prev_hash}::{data_hash}::{timestamp}::{nonce}"
        current_hash = calculate_sha256(block_content)

        block = BlockchainBlock(
            index=new_index,
            timestamp=timestamp,
            previous_hash=prev_hash,
            current_hash=current_hash,
            data_hash=data_hash,
            payload=inspection_payload,
            nonce=nonce
        )
        self.db.add(block)
        self.db.commit()
        self.db.refresh(block)
        return block

    def verify_record_integrity(self, record_id: int) -> dict:
        """
        Recalculates SHA-256 fingerprint from the active database row
        and checks against the immutable blockchain block.
        """
        record = self.db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
        if not record:
            return {"status": "ERROR", "message": "Record not found"}

        if record.blockchain_block_index is None:
            return {"status": "UNRECORDED", "message": "No blockchain record associated"}

        block = self.db.query(BlockchainBlock).filter(BlockchainBlock.index == record.blockchain_block_index).first()
        if not block:
            return {"status": "ERROR", "message": f"Block #{record.blockchain_block_index} missing from ledger"}

        # Extract current values from DB
        ext = record.extracted_data or {}
        mrp_val = ext.get("mrp", {}).get("value")
        net_val = ext.get("net_quantity", {}).get("value")
        net_unit = ext.get("net_quantity", {}).get("unit")
        image_hash = calculate_file_sha256(record.original_image_path)

        if hasattr(record.timestamp, "strftime"):
            ts_str = record.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            ts_str = str(record.timestamp)

        viol_str = json.dumps(record.violations, sort_keys=True) if record.violations else ""

        current_payload = canonical_record_payload(
            inspection_id=record.inspection_id,
            timestamp=ts_str,
            inspector_id=record.inspector_id,
            shop_name=record.shop_name,
            image_hash=image_hash,
            mrp=mrp_val,
            net_qty=net_val,
            net_unit=net_unit,
            verdict=record.verdict,
            violations_summary=viol_str
        )

        current_data_hash = calculate_sha256(json.dumps(current_payload, sort_keys=True))
        recorded_data_hash = block.data_hash

        is_valid = (current_data_hash == recorded_data_hash)

        return {
            "is_valid": is_valid,
            "status": "VERIFIED_AUTHENTIC" if is_valid else "TAMPER_DETECTED",
            "inspection_id": record.inspection_id,
            "block_index": block.index,
            "blockchain_block_hash": block.current_hash,
            "recorded_blockchain_data_hash": recorded_data_hash,
            "current_recalculated_hash": current_data_hash,
            "is_tampered_flag": record.is_tampered,
            "original_recorded_payload": block.payload,
            "current_db_payload": current_payload,
            "mismatch_detected": not is_valid
        }

    def simulate_tamper(self, record_id: int, fake_mrp: float = 40.0) -> dict:
        """
        Alters the database record directly (e.g. modifying MRP)
        without altering the blockchain, to demonstrate tamper detection.
        """
        record = self.db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
        if not record:
            return {"error": "Record not found"}

        # Store backup of original MRP
        if record.original_mrp_for_tamper_demo is None:
            orig = record.extracted_data.get("mrp", {}).get("value")
            record.original_mrp_for_tamper_demo = orig

        # Mutate extracted_data JSON
        data = dict(record.extracted_data)
        if "mrp" in data:
            data["mrp"] = dict(data["mrp"])
            data["mrp"]["value"] = fake_mrp
            data["mrp"]["raw"] = f"MRP: Rs. {fake_mrp}"

        record.extracted_data = data
        record.is_tampered = True
        self.db.commit()

        # Immediately test integrity to show the effect
        return self.verify_record_integrity(record_id)

    def revert_tamper(self, record_id: int) -> dict:
        record = self.db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
        if not record or not record.is_tampered:
            return {"message": "No tampering active"}

        orig_mrp = record.original_mrp_for_tamper_demo
        data = dict(record.extracted_data)
        if "mrp" in data and orig_mrp is not None:
            data["mrp"] = dict(data["mrp"])
            data["mrp"]["value"] = orig_mrp
            data["mrp"]["raw"] = f"MRP: Rs. {orig_mrp}"

        record.extracted_data = data
        record.is_tampered = False
        record.original_mrp_for_tamper_demo = None
        self.db.commit()

        return self.verify_record_integrity(record_id)

    def get_recent_blocks(self, limit: int = 15) -> list:
        blocks = self.db.query(BlockchainBlock).order_by(BlockchainBlock.index.desc()).limit(limit).all()
        return [
            {
                "index": b.index,
                "timestamp": b.timestamp,
                "previous_hash": b.previous_hash,
                "current_hash": b.current_hash,
                "data_hash": b.data_hash,
                "payload": b.payload,
                "nonce": b.nonce
            }
            for b in blocks
        ]
