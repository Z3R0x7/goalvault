from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, IntegerField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from app.extensions import db
from app.models.user import User
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.models.audit_log import AuditLog
from app.models.escalation import Escalation
from app.models.cycle_config import CycleConfig
from app.utils.decorators import role_required
from app.services.audit_service import AuditService
from app.services.escalation_service import EscalationService
from app.services.goal_service import GoalService
from app.models.escalation_settings import EscalationSettings

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

PHASES = [
    ("goal_setting", "Goal Setting"),
    ("Q1", "Q1 Check-in"),
    ("Q2", "Q2 Check-in"),
    ("Q3", "Q3 Check-in"),
    ("Q4", "Q4 / Annual"),
]


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Optional()])
    role = SelectField(
        "Role",
        choices=[("employee", "Employee"), ("manager", "Manager"), ("admin", "Admin")],
    )
    department = StringField("Department", validators=[Optional()])
    manager_id = SelectField("Manager", coerce=int, validators=[Optional()])
    submit = SubmitField("Add User")


class CycleForm(FlaskForm):
    phase = SelectField("Phase", choices=PHASES, validators=[DataRequired()])
    window_open = DateField("Window Opens", validators=[Optional()])
    window_close = DateField("Window Closes", validators=[Optional()])
    escalation_days = IntegerField(
        "Escalation Days", validators=[Optional(), NumberRange(min=1)]
    )
    submit = SubmitField("Save")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    employees = User.query.filter_by(role="employee", is_active=True).count()
    total_goals = Goal.query.count()
    approved = Goal.query.filter(Goal.status.in_(["approved", "locked"])).count()
    submitted_goals = Goal.query.filter_by(status="submitted").count()
    checkins = Achievement.query.filter(Achievement.checkin_at.isnot(None)).count()
    return render_template(
        "admin/dashboard.html",
        employees=employees,
        total_goals=total_goals,
        approved=approved,
        submitted=submitted_goals,
        checkins=checkins,
    )


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def users():
    form = UserForm()
    managers = User.query.filter(User.role.in_(["manager", "admin"])).all()
    form.manager_id.choices = [(0, "— None —")] + [(m.id, m.name) for m in managers]

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email already exists.", "danger")
        else:
            user = User(
                name=form.name.data,
                email=form.email.data.lower(),
                role=form.role.data,
                department=form.department.data,
                manager_id=form.manager_id.data or None,
            )
            pwd = form.password.data or "ChangeMe@123"
            user.set_password(pwd)
            db.session.add(user)
            db.session.commit()
            AuditService.log(
                "USER_CREATED",
                "user",
                user.id,
                current_user.id,
                ip_address=request.remote_addr,
            )
            flash(f"User {user.name} created.", "success")
            return redirect(url_for("admin.users"))

    all_users = User.query.order_by(User.role, User.name).all()
    return render_template("admin/users.html", users=all_users, form=form)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Cannot deactivate yourself.", "warning")
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"User {'activated' if user.is_active else 'deactivated'}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/cycle-config", methods=["GET", "POST"])
@login_required
@role_required("admin")
def cycle_config():
    form = CycleForm()
    if form.validate_on_submit():
        config = CycleConfig.query.filter_by(
            cycle_year=current_app.config["CYCLE_YEAR"], phase=form.phase.data
        ).first()
        if not config:
            config = CycleConfig(
                cycle_year=current_app.config["CYCLE_YEAR"], phase=form.phase.data
            )
            db.session.add(config)
        config.window_open = form.window_open.data
        config.window_close = form.window_close.data
        config.escalation_days = form.escalation_days.data or 7
        db.session.commit()
        flash("Cycle configuration saved.", "success")
        return redirect(url_for("admin.cycle_config"))

    configs = CycleConfig.query.filter_by(
        cycle_year=current_app.config["CYCLE_YEAR"]
    ).all()
    return render_template("admin/cycle_config.html", configs=configs, form=form)


@admin_bp.route("/audit-trail")
@login_required
@role_required("admin")
def audit_trail():
    page = request.args.get("page", 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.id.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    return render_template("admin/audit_trail.html", logs=logs)


@admin_bp.route("/completion")
@login_required
@role_required("admin")
def completion():
    employees = User.query.filter_by(role="employee", is_active=True).all()
    stats = []
    for emp in employees:
        goals = Goal.query.filter_by(employee_id=emp.id).all()
        submitted = sum(1 for g in goals if g.status in ("submitted", "approved", "locked"))
        approved = sum(1 for g in goals if g.status in ("approved", "locked"))
        checkins = Achievement.query.join(Goal).filter(
            Goal.employee_id == emp.id, Achievement.checkin_at.isnot(None)
        ).count()
        stats.append(
            {
                "employee": emp,
                "goals_total": len(goals),
                "submitted": submitted,
                "approved": approved,
                "checkins": checkins,
            }
        )
    total = len(employees) or 1
    submitted_pct = sum(1 for s in stats if s["submitted"] > 0) / total * 100
    approved_pct = sum(1 for s in stats if s["approved"] > 0) / total * 100
    return render_template(
        "admin/completion.html",
        stats=stats,
        submitted_pct=round(submitted_pct, 1),
        approved_pct=round(approved_pct, 1),
    )


@admin_bp.route("/security")
@login_required
@role_required("admin")
def security():
    failed_logs = (
        AuditLog.query.filter(AuditLog.action == "LOGIN_FAILED")
        .order_by(AuditLog.timestamp.desc())
        .limit(50)
        .all()
    )
    escalations = Escalation.query.filter_by(resolved=False).order_by(
        Escalation.triggered_at.desc()
    ).all()
    return render_template(
        "admin/security.html", failed_logs=failed_logs, escalations=escalations
    )


@admin_bp.route("/goals/<int:goal_id>/unlock", methods=["POST"])
@login_required
@role_required("admin")
def unlock_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    old_status = goal.status
    goal.status = "rework"
    goal.locked_at = None
    db.session.commit()
    AuditService.log(
        "GOAL_UNLOCKED",
        "goal",
        goal.id,
        current_user.id,
        old_value={"status": old_status},
        new_value={"status": "rework"},
        ip_address=request.remote_addr,
    )
    flash("Goal unlocked for editing.", "success")
    return redirect(url_for("admin.completion"))


@admin_bp.route("/analytics")
@login_required
@role_required("admin")
def analytics():
    return render_template("admin/analytics.html")


@admin_bp.route("/escalations", methods=["GET", "POST"])
@login_required
@role_required("admin")
def escalations():
    settings = EscalationSettings.get()
    if request.method == "POST":
        settings.goal_submit_days = int(request.form.get("goal_submit_days", 5))
        settings.goal_approve_days = int(request.form.get("goal_approve_days", 7))
        settings.checkin_days = int(request.form.get("checkin_days", 7))
        db.session.commit()
        flash("Escalation thresholds saved.", "success")
        return redirect(url_for("admin.escalations"))

    active = Escalation.query.filter_by(resolved=False).order_by(
        Escalation.triggered_at.desc()
    ).all()
    by_type = {
        "goal_not_submitted": [e for e in active if e.rule_type == "goal_not_submitted"],
        "goal_not_approved": [e for e in active if e.rule_type == "goal_not_approved"],
        "checkin_missed": [e for e in active if e.rule_type == "checkin_missed"],
    }
    return render_template(
        "admin/escalations.html", settings=settings, by_type=by_type
    )


@admin_bp.route("/notifications")
@login_required
@role_required("admin")
def notifications():
    return render_template("admin/notifications.html")


@admin_bp.route("/trigger-escalation", methods=["POST"])
@login_required
@role_required("admin")
def trigger_escalation():
    result = EscalationService.run_all_checks()
    flash(
        f"Escalation check complete: {result['total']} new escalation(s).",
        "success",
    )
    return redirect(url_for("admin.escalations"))
