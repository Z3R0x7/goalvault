from datetime import datetime
from app.extensions import db


class Escalation(db.Model):
    __tablename__ = "escalations"

    id = db.Column(db.Integer, primary_key=True)
    rule_type = db.Column(db.String(50))  # goal_not_submitted, goal_not_approved, checkin_missed
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    notified_at = db.Column(db.DateTime)
    resolved = db.Column(db.Boolean, default=False)
    details = db.Column(db.Text)

    target_user = db.relationship("User", backref="escalations")
