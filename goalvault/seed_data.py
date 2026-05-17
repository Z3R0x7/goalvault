from datetime import datetime, date
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.models.cycle_config import CycleConfig
from app.services.audit_service import AuditService
from app.models.escalation_settings import EscalationSettings


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(
            name="Admin User",
            email="admin@goalvault.com",
            role="admin",
            department="HR",
        )
        admin.set_password("Demo@123")

        manager = User(
            name="Manager User",
            email="manager@goalvault.com",
            role="manager",
            department="Engineering",
        )
        manager.set_password("Demo@123")

        employee = User(
            name="Employee User",
            email="employee@goalvault.com",
            role="employee",
            department="Engineering",
        )
        employee.set_password("Demo@123")

        db.session.add_all([admin, manager, employee])
        db.session.flush()

        employee.manager_id = manager.id
        manager.manager_id = admin.id

        year = app.config.get("CYCLE_YEAR", 2025)
        today = date.today()
        phases = [
            ("goal_setting", date(year, 1, 1), date(year, 12, 31), 7),
            ("Q1", date(year, 7, 1), date(year, 7, 31), 7),
            ("Q2", date(year, 10, 1), date(year, 10, 31), 7),
            ("Q3", date(year + 1, 1, 1), date(year + 1, 1, 31), 7),
            ("Q4", date(year + 1, 3, 1), date(year + 1, 4, 30), 7),
        ]
        if today.year != year:
            phases[0] = ("goal_setting", today.replace(month=1, day=1), date(today.year, 12, 31), 7)
        for phase, open_d, close_d, esc in phases:
            db.session.add(
                CycleConfig(
                    cycle_year=year,
                    phase=phase,
                    window_open=open_d,
                    window_close=close_d,
                    escalation_days=esc,
                )
            )

        goals_data = [
            {
                "title": "Increase Q1 Revenue by 15%",
                "description": "Drive new business in enterprise segment through outbound campaigns.",
                "thrust_area": "Revenue Growth",
                "uom_type": "numeric_min",
                "target": 15,
                "weightage": 30,
                "status": "approved",
            },
            {
                "title": "Reduce Customer Response TAT",
                "description": "Lower average first-response time for support tickets.",
                "thrust_area": "Customer Experience",
                "uom_type": "numeric_max",
                "target": 4,
                "weightage": 25,
                "status": "approved",
            },
            {
                "title": "Launch Internal Knowledge Portal",
                "description": "Deliver MVP knowledge base by end of Q2.",
                "thrust_area": "Innovation",
                "uom_type": "timeline",
                "target": 1,
                "weightage": 15,
                "status": "approved",
            },
            {
                "title": "Zero Safety Incidents",
                "description": "Maintain zero recordable safety incidents.",
                "thrust_area": "Operational Excellence",
                "uom_type": "zero",
                "target": 0,
                "weightage": 10,
                "status": "submitted",
            },
        ]

        for gdata in goals_data:
            goal = Goal(
                employee_id=employee.id,
                cycle_year=year,
                locked_at=datetime.utcnow() if gdata["status"] == "approved" else None,
                **gdata,
            )
            db.session.add(goal)
            db.session.flush()

            if goal.status == "approved":
                ach = Achievement(
                    goal_id=goal.id,
                    quarter="Q1",
                    actual_value=12 if goal.uom_type == "numeric_min" else 3.5,
                    status="on_track",
                    submitted_at=datetime.utcnow(),
                )
                ach.compute_progress_score()
                db.session.add(ach)

        db.session.add(EscalationSettings(goal_submit_days=5, goal_approve_days=7, checkin_days=7))
        db.session.commit()

        AuditService.log("SYSTEM_SEED", "system", 0, admin.id, new_value={"seed": True})
        AuditService.log("GOAL_APPROVED", "goal", 1, manager.id, new_value={"demo": True})

        print("Seed complete!")
        print("  Admin:    admin@goalvault.com / Demo@123")
        print("  Manager:  manager@goalvault.com / Demo@123")
        print("  Employee: employee@goalvault.com / Demo@123")


if __name__ == "__main__":
    seed()
