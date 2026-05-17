from app.extensions import db


class EscalationSettings(db.Model):
    __tablename__ = "escalation_settings"

    id = db.Column(db.Integer, primary_key=True)
    goal_submit_days = db.Column(db.Integer, default=5)
    goal_approve_days = db.Column(db.Integer, default=7)
    checkin_days = db.Column(db.Integer, default=7)

    @staticmethod
    def get():
        row = EscalationSettings.query.first()
        if not row:
            row = EscalationSettings()
            db.session.add(row)
            db.session.commit()
        return row
