from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.models.escalation import Escalation
from app.models.cycle_config import CycleConfig


class EscalationService:
    @staticmethod
    def _create_escalation(rule_type, user_id, details):
        existing = Escalation.query.filter_by(
            rule_type=rule_type, target_user_id=user_id, resolved=False
        ).first()
        if existing:
            return existing
        esc = Escalation(
            rule_type=rule_type,
            target_user_id=user_id,
            details=details,
            triggered_at=datetime.utcnow(),
        )
        db.session.add(esc)
        return esc

    @staticmethod
    def check_goal_not_submitted():
        config = CycleConfig.query.filter_by(phase="goal_setting").first()
        if not config or not config.window_open:
            return []
        threshold = config.window_open + timedelta(days=config.escalation_days or 7)
        if datetime.utcnow().date() < threshold:
            return []

        created = []
        employees = User.query.filter_by(role="employee", is_active=True).all()
        for emp in employees:
            submitted = Goal.query.filter(
                Goal.employee_id == emp.id,
                Goal.status.in_(["submitted", "approved", "locked"]),
            ).count()
            if submitted == 0:
                esc = EscalationService._create_escalation(
                    "goal_not_submitted",
                    emp.id,
                    f"{emp.name} has not submitted any goals",
                )
                created.append(esc)
        db.session.commit()
        return created

    @staticmethod
    def check_goal_not_approved():
        days = 7
        threshold = datetime.utcnow() - timedelta(days=days)
        created = []
        pending = Goal.query.filter(
            Goal.status == "submitted", Goal.updated_at <= threshold
        ).all()
        for goal in pending:
            esc = EscalationService._create_escalation(
                "goal_not_approved",
                goal.employee.manager_id or goal.employee_id,
                f"Goal '{goal.title}' pending approval for {days}+ days",
            )
            created.append(esc)
        db.session.commit()
        return created

    @staticmethod
    def check_checkin_missed():
        created = []
        for phase, quarter in [("Q1", "Q1"), ("Q2", "Q2"), ("Q3", "Q3"), ("Q4", "Q4")]:
            config = CycleConfig.query.filter_by(phase=phase).first()
            if not config or not config.window_close:
                continue
            if datetime.utcnow().date() <= config.window_close:
                continue

            employees = User.query.filter_by(role="employee", is_active=True).all()
            for emp in employees:
                goals = Goal.query.filter_by(
                    employee_id=emp.id, status="approved"
                ).all()
                for goal in goals:
                    ach = Achievement.query.filter_by(
                        goal_id=goal.id, quarter=quarter
                    ).first()
                    if not ach or not ach.submitted_at:
                        esc = EscalationService._create_escalation(
                            "checkin_missed",
                            emp.id,
                            f"Missing {quarter} check-in for goal '{goal.title}'",
                        )
                        created.append(esc)
        db.session.commit()
        return created

    @staticmethod
    def run_all_checks():
        r1 = EscalationService.check_goal_not_submitted()
        r2 = EscalationService.check_goal_not_approved()
        r3 = EscalationService.check_checkin_missed()
        return {
            "goal_not_submitted": len(r1),
            "goal_not_approved": len(r2),
            "checkin_missed": len(r3),
            "total": len(r1) + len(r2) + len(r3),
        }
