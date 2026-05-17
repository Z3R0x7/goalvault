from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.goal import Goal
from app.models.achievement import Achievement


class AnalyticsService:
    @staticmethod
    def get_org_summary(cycle_year=None):
        year = cycle_year or current_app.config.get("CYCLE_YEAR", 2025)
        employees = User.query.filter_by(role="employee", is_active=True).all()
        total_emp = len(employees) or 1

        submitted = 0
        approved = 0
        checkin_done = 0
        for emp in employees:
            goals = Goal.query.filter_by(employee_id=emp.id, cycle_year=year).all()
            if any(g.status in ("submitted", "approved", "locked") for g in goals):
                submitted += 1
            if any(g.status in ("approved", "locked") for g in goals):
                approved += 1
            if Achievement.query.join(Goal).filter(
                Goal.employee_id == emp.id, Achievement.checkin_at.isnot(None)
            ).count():
                checkin_done += 1

        funnel = {
            "labels": ["Goals Submitted", "Goals Approved", "Check-ins Done"],
            "values": [
                round(submitted / total_emp * 100, 1),
                round(approved / total_emp * 100, 1),
                round(checkin_done / total_emp * 100, 1),
            ],
        }

        departments = {}
        for emp in employees:
            dept = emp.department or "Unassigned"
            if dept not in departments:
                departments[dept] = {
                    "employees": 0,
                    "approved_pct": 0,
                    "q_scores": {"Q1": [], "Q2": [], "Q3": [], "Q4": []},
                }
            departments[dept]["employees"] += 1
            goals = Goal.query.filter_by(
                employee_id=emp.id, cycle_year=year
            ).filter(Goal.status.in_(["approved", "locked"])).all()
            if goals:
                departments[dept]["approved_pct"] += 1
            for q in ["Q1", "Q2", "Q3", "Q4"]:
                for g in goals:
                    ach = Achievement.query.filter_by(goal_id=g.id, quarter=q).first()
                    if ach and ach.progress_score is not None:
                        departments[dept]["q_scores"][q].append(ach.progress_score)

        heatmap = []
        for dept, data in departments.items():
            emp_n = data["employees"] or 1
            row = {
                "department": dept,
                "approved_pct": round(data["approved_pct"] / emp_n * 100, 0),
                "quarters": {},
            }
            for q in ["Q1", "Q2", "Q3", "Q4"]:
                scores = data["q_scores"][q]
                row["quarters"][q] = round(sum(scores) / len(scores), 0) if scores else None
            heatmap.append(row)

        score_buckets = {"high": 0, "mid": 0, "low": 0}
        for emp in employees:
            goals = Goal.query.filter_by(
                employee_id=emp.id, cycle_year=year
            ).filter(Goal.status.in_(["approved", "locked"])).all()
            scores = []
            for g in goals:
                ach = Achievement.query.filter_by(goal_id=g.id, quarter="Q1").first()
                if ach and ach.progress_score is not None:
                    scores.append(ach.progress_score)
            if not scores:
                continue
            avg = sum(scores) / len(scores)
            if avg >= 80:
                score_buckets["high"] += 1
            elif avg >= 50:
                score_buckets["mid"] += 1
            else:
                score_buckets["low"] += 1

        distribution = {
            "labels": ["Top Performers (80%+)", "On Track (50-79%)", "At Risk (<50%)"],
            "values": [
                score_buckets["high"],
                score_buckets["mid"],
                score_buckets["low"],
            ],
        }

        return {
            "cycle_year": year,
            "funnel": funnel,
            "heatmap": heatmap,
            "distribution": distribution,
            "totals": {
                "employees": total_emp,
                "submitted_pct": funnel["values"][0],
                "approved_pct": funnel["values"][1],
                "checkin_pct": funnel["values"][2],
            },
        }
