from datetime import datetime
from app.extensions import db


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    thrust_area = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    uom_type = db.Column(db.String(20), nullable=False)  # numeric_min, numeric_max, timeline, zero
    target = db.Column(db.Float)
    weightage = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="draft")  # draft, submitted, approved, rework, locked
    is_shared = db.Column(db.Boolean, default=False)
    shared_from_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=True)
    cycle_year = db.Column(db.Integer, default=2025)
    manager_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    locked_at = db.Column(db.DateTime)

    shared_from = db.relationship("Goal", remote_side=[id], backref="copies")
    achievements = db.relationship("Achievement", backref="goal", cascade="all, delete-orphan")

    @property
    def is_editable(self):
        return self.status in ("draft", "rework")

    @property
    def is_locked(self):
        return self.status in ("approved", "locked")
