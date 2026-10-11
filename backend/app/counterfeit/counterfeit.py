from datetime import datetime
from sqlalchemy.orm import Session
from ..database.models import ManufacturerBatch, UnitSerial

class CounterfeitExtension:
    @staticmethod
    def register_batch(
        batch_id: str,
        product_name: str,
        manufacturer_name: str,
        mrp: float,
        unit_count: int,
        prefix: str,
        db: Session
    ) -> dict:
        """
        Registers a genuine manufacturer batch and generates serialized unit IDs.
        """
        # Check if batch exists
        existing = db.query(ManufacturerBatch).filter(ManufacturerBatch.batch_id == batch_id).first()
        if existing:
            return {"error": f"Batch {batch_id} already registered"}

        batch = ManufacturerBatch(
            batch_id=batch_id,
            product_name=product_name,
            manufacturer_name=manufacturer_name,
            mrp=mrp,
            total_units=unit_count,
            registered_at=datetime.utcnow()
        )
        db.add(batch)

        # Generate unique serial units (e.g. ABC001, ABC002...)
        serials_created = []
        for i in range(1, unit_count + 1):
            s_id = f"{prefix.upper()}{i:03d}"
            serial = UnitSerial(
                serial_id=s_id,
                batch_id=batch_id,
                product_name=product_name,
                manufacturer_name=manufacturer_name,
                scan_count=0,
                status="GENUINE_UNSCANNED"
            )
            db.add(serial)
            serials_created.append(s_id)

        db.commit()
        return {
            "batch_id": batch_id,
            "product_name": product_name,
            "manufacturer_name": manufacturer_name,
            "total_units": unit_count,
            "serials_sample": serials_created[:5]
        }

    @staticmethod
    def verify_serial(serial_id: str, shop_name: str, db: Session) -> dict:
        """
        Verifies unique physical serial ID against registered manufacturer registry.
        Detects if same unique ID is scanned across different shops (duplicate clone attack).
        """
        clean_id = serial_id.strip().upper()
        unit = db.query(UnitSerial).filter(UnitSerial.serial_id == clean_id).first()

        if not unit:
            return {
                "verdict": "SUSPICIOUS_UNREGISTERED",
                "serial_id": clean_id,
                "is_genuine": False,
                "title": "Unregistered Serial ID",
                "message": f"Serial ID '{clean_id}' does not exist in any registered manufacturer database. High risk of counterfeit goods.",
                "color": "red"
            }

        now = datetime.utcnow()
        unit.scan_count += 1

        if unit.scan_count == 1:
            unit.status = "VERIFIED_AUTHENTIC"
            unit.last_scanned_shop = shop_name
            unit.first_scanned_at = now
            db.commit()
            return {
                "verdict": "VERIFIED_AUTHENTIC",
                "serial_id": clean_id,
                "is_genuine": True,
                "product_name": unit.product_name,
                "manufacturer": unit.manufacturer_name,
                "batch_id": unit.batch_id,
                "scan_count": 1,
                "first_scanned_shop": shop_name,
                "message": f"Genuine product verified. Unit registered to {unit.manufacturer_name} under Batch {unit.batch_id}.",
                "color": "green"
            }
        else:
            # Duplicate scan detected
            is_different_shop = (unit.last_scanned_shop and unit.last_scanned_shop != shop_name)
            unit.status = "DUPLICATE_SUSPICIOUS"
            db.commit()
            return {
                "verdict": "DUPLICATE_SUSPICIOUS",
                "serial_id": clean_id,
                "is_genuine": False,
                "product_name": unit.product_name,
                "manufacturer": unit.manufacturer_name,
                "batch_id": unit.batch_id,
                "scan_count": unit.scan_count,
                "previous_shop": unit.last_scanned_shop,
                "current_shop": shop_name,
                "title": "Duplicate Serial ID Detected!",
                "message": f"ALERT: Unit ID '{clean_id}' was previously recorded at '{unit.last_scanned_shop}' and is now appearing at '{shop_name}'. Physical clone or replicated barcode suspected!",
                "color": "red"
            }

    @staticmethod
    def list_batches(db: Session) -> list:
        batches = db.query(ManufacturerBatch).order_by(ManufacturerBatch.registered_at.desc()).all()
        result = []
        for b in batches:
            serials = db.query(UnitSerial).filter(UnitSerial.batch_id == b.batch_id).all()
            result.append({
                "batch_id": b.batch_id,
                "product_name": b.product_name,
                "manufacturer_name": b.manufacturer_name,
                "mrp": b.mrp,
                "total_units": b.total_units,
                "registered_at": b.registered_at.isoformat() if b.registered_at else None,
                "serials": [{"serial_id": s.serial_id, "scan_count": s.scan_count, "status": s.status, "last_scanned_shop": s.last_scanned_shop} for s in serials]
            })
        return result
