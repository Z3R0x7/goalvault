from app.extensions import db


class CycleConfig(db.Model):
    __tablename__ = "cycle_config"

    id = db.Column(db.Integer, primary_key=True)
    cycle_year = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.String(20), nullable=False)  # goal_setting, Q1, Q2, Q3, Q4
    window_open = db.Column(db.Date)
    window_close = db.Column(db.Date)
    escalation_days = db.Column(db.Integer, default=7)
