import hashlib
import json
from datetime import datetime
from flask import request
from app.extensions import db
from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def _compute_hash(entry_data: dict, prev_hash: str) -> str:
        payload = json.dumps(entry_data, sort_keys=True, default=str) + prev_hash
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def log(
        action: str,
        entity_type: str,
        entity_id: int,
        user_id: int,
        old_value=None,
        new_value=None,
        ip_address=None,
    ):
        last_entry = AuditLog.query.order_by(AuditLog.id.desc()).first()
        prev_hash = last_entry.entry_hash if last_entry else "GENESIS"

        ip = ip_address or (request.remote_addr if request else None)
        ts = datetime.utcnow()
        entry_data = {
            "timestamp": ts.isoformat(),
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "old_value": old_value,
            "new_value": new_value,
            "ip_address": ip,
        }

        entry_hash = AuditService._compute_hash(entry_data, prev_hash)

        log_entry = AuditLog(
            timestamp=ts,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=json.dumps(old_value) if old_value is not None else None,
            new_value=json.dumps(new_value) if new_value is not None else None,
            ip_address=ip,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

    @staticmethod
    def verify_chain() -> dict:
        entries = AuditLog.query.order_by(AuditLog.id.asc()).all()
        prev_hash = "GENESIS"
        broken_at = None

        for entry in entries:
            entry_data = {
                "timestamp": entry.timestamp.isoformat(),
                "user_id": entry.user_id,
                "action": entry.action,
                "entity_type": entry.entity_type,
                "entity_id": entry.entity_id,
                "old_value": json.loads(entry.old_value) if entry.old_value else None,
                "new_value": json.loads(entry.new_value) if entry.new_value else None,
                "ip_address": entry.ip_address,
            }
            expected_hash = AuditService._compute_hash(entry_data, prev_hash)

            if expected_hash != entry.entry_hash:
                broken_at = entry.id
                break
            prev_hash = entry.entry_hash

        return {
            "intact": broken_at is None,
            "total_entries": len(entries),
            "broken_at_id": broken_at,
            "message": "Chain intact ✓"
            if broken_at is None
            else f"Chain broken at entry #{broken_at} ✗",
        }
