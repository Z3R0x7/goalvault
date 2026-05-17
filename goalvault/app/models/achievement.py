from datetime import datetime
from app.extensions import db


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    quarter = db.Column(db.String(5), nullable=False)  # Q1, Q2, Q3, Q4
    actual_value = db.Column(db.Float)
    status = db.Column(db.String(20), default="not_started")  # not_started, on_track, completed
    progress_score = db.Column(db.Float, default=0.0)
    submitted_at = db.Column(db.DateTime)
    manager_comment = db.Column(db.Text)
    checkin_at = db.Column(db.DateTime)
    completion_date = db.Column(db.Date)

    def compute_progress_score(self):
        goal = self.goal
        if not goal or goal.target is None:
            self.progress_score = 0.0
            return 0.0

        if goal.uom_type == "numeric_min":
            score = min((self.actual_value or 0) / goal.target * 100, 100) if goal.target else 0
        elif goal.uom_type == "numeric_max":
            actual = self.actual_value or 0
            score = min((goal.target / actual) * 100, 100) if actual > 0 else 0
        elif goal.uom_type == "zero":
            score = 100.0 if (self.actual_value or 0) == 0 else 0.0
        elif goal.uom_type == "timeline":
            if self.status == "completed":
                score = 100.0
            elif self.status == "on_track":
                score = 75.0
            else:
                score = 25.0 if self.actual_value else 0.0
        else:
            score = 0.0

        self.progress_score = round(score, 2)
        return self.progress_score
