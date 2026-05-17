from datetime import date
from flask import current_app
from app.extensions import db
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.models.cycle_config import CycleConfig


class GoalService:
    MAX_GOALS = 8
    MIN_WEIGHTAGE = 10.0

    @staticmethod
    def count_goals(employee_id, cycle_year=None):
        year = cycle_year or current_app.config.get("CYCLE_YEAR", 2025)
        return Goal.query.filter_by(
            employee_id=employee_id, cycle_year=year
        ).count()

    @staticmethod
    def total_weightage(employee_id, exclude_goal_id=None, cycle_year=None):
        year = cycle_year or current_app.config.get("CYCLE_YEAR", 2025)
        q = Goal.query.filter_by(employee_id=employee_id, cycle_year=year)
        if exclude_goal_id:
            q = q.filter(Goal.id != exclude_goal_id)
        return sum(g.weightage for g in q.all())

    @staticmethod
    def validate_weightage(employee_id, new_weightage, exclude_goal_id=None):
        total = GoalService.total_weightage(employee_id, exclude_goal_id) + new_weightage
        errors = []
        if new_weightage < GoalService.MIN_WEIGHTAGE:
            errors.append(f"Minimum weightage per goal is {GoalService.MIN_WEIGHTAGE}%")
        if total > 100:
            errors.append(f"Total weightage would be {total:.1f}% (max 100%)")
        return errors, total

    @staticmethod
    def remaining_weightage(employee_id, exclude_goal_id=None, cycle_year=None):
        used = GoalService.total_weightage(employee_id, exclude_goal_id, cycle_year)
        return max(0.0, 100.0 - used)

    @staticmethod
    def can_add_goal(employee_id):
        if GoalService.count_goals(employee_id) >= GoalService.MAX_GOALS:
            return False, f"Maximum {GoalService.MAX_GOALS} goals allowed"
        if GoalService.remaining_weightage(employee_id) < GoalService.MIN_WEIGHTAGE:
            return (
                False,
                "Weightage is already at 100%. Edit or remove a draft goal to free capacity.",
            )
        return True, None

    @staticmethod
    def is_window_open(phase):
        today = date.today()
        config = CycleConfig.query.filter_by(phase=phase).first()
        if not config:
            return True
        if config.window_open and today < config.window_open:
            return False
        if config.window_close and today > config.window_close:
            return False
        return True

    @staticmethod
    def get_employee_stats(employee_id, cycle_year=None):
        year = cycle_year or current_app.config.get("CYCLE_YEAR", 2025)
        goals = Goal.query.filter_by(employee_id=employee_id, cycle_year=year).all()
        approved = [g for g in goals if g.status in ("approved", "locked")]
        pending = [g for g in goals if g.status in ("submitted", "draft", "rework")]
        scores = []
        for g in approved:
            for a in g.achievements:
                if a.progress_score:
                    scores.append(a.progress_score)
        avg_progress = sum(scores) / len(scores) if scores else 0
        return {
            "total": len(goals),
            "approved": len(approved),
            "pending": len(pending),
            "weightage_used": sum(g.weightage for g in goals),
            "avg_progress": round(avg_progress, 1),
        }

    @staticmethod
    def get_quarter_progress(employee_id, quarter="Q1", cycle_year=None):
        year = cycle_year or current_app.config.get("CYCLE_YEAR", 2025)
        goals = Goal.query.filter_by(
            employee_id=employee_id, cycle_year=year
        ).filter(Goal.status.in_(["approved", "locked"])).all()
        items = []
        weighted_sum = 0.0
        total_weight = 0.0
        for g in goals:
            ach = Achievement.query.filter_by(goal_id=g.id, quarter=quarter).first()
            score = ach.progress_score if ach and ach.progress_score is not None else 0
            items.append({
                "title": g.title,
                "weightage": g.weightage,
                "target": g.target,
                "score": score,
                "status": ach.status if ach else "not_started",
            })
            weighted_sum += score * g.weightage
            total_weight += g.weightage
        weighted_score = round(weighted_sum / total_weight, 1) if total_weight else 0
        return {"entries": items, "weighted_score": weighted_score, "quarter": quarter}
