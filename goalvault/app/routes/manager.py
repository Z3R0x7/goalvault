from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.extensions import db
from app.models.user import User
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.utils.decorators import role_required
from app.services.audit_service import AuditService
from app.services.ai_service import AIService

manager_bp = Blueprint("manager", __name__, url_prefix="/manager")


class ApprovalForm(FlaskForm):
    target = FloatField("Target", validators=[Optional(), NumberRange(min=0)])
    weightage = FloatField("Weightage", validators=[Optional(), NumberRange(min=10, max=100)])
    comment = TextAreaField("Comment", validators=[Optional()])
    submit = SubmitField("Approve")


class ReturnForm(FlaskForm):
    comment = TextAreaField("Return Comment", validators=[DataRequired()])
    submit = SubmitField("Return for Rework")


class CheckinForm(FlaskForm):
    comment = TextAreaField("Check-in Comment", validators=[DataRequired()])
    submit = SubmitField("Save Check-in")


@manager_bp.route("/dashboard")
@login_required
@role_required("manager")
def dashboard():
    team = User.query.filter_by(manager_id=current_user.id, is_active=True).all()
    pending = Goal.query.filter(
        Goal.employee_id.in_([e.id for e in team] or [0]),
        Goal.status == "submitted",
    ).count()
    approved = Goal.query.filter(
        Goal.employee_id.in_([e.id for e in team] or [0]),
        Goal.status.in_(["approved", "locked"]),
    ).count()
    return render_template(
        "manager/dashboard.html",
        team=team,
        pending_count=pending,
        approved_count=approved,
    )


@manager_bp.route("/team")
@login_required
@role_required("manager")
def team_goals():
    team = User.query.filter_by(manager_id=current_user.id, is_active=True).all()
    data = []
    for emp in team:
        goals = Goal.query.filter_by(employee_id=emp.id).all()
        data.append({"employee": emp, "goals": goals})
    return render_template("manager/team_goals.html", team_data=data)


@manager_bp.route("/approvals")
@login_required
@role_required("manager")
def approvals():
    team_ids = [
        e.id
        for e in User.query.filter_by(manager_id=current_user.id).all()
    ]
    pending_goals = Goal.query.filter(
        Goal.employee_id.in_(team_ids or [0]), Goal.status == "submitted"
    ).all()
    return render_template("manager/approval.html", goals=pending_goals)


@manager_bp.route("/goals/<int:goal_id>/approve", methods=["POST"])
@login_required
@role_required("manager")
def approve_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    emp = User.query.get(goal.employee_id)
    if emp.manager_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("manager.approvals"))

    form = ApprovalForm()
    if form.target.data is not None:
        goal.target = form.target.data
    if form.weightage.data is not None:
        goal.weightage = form.weightage.data

    goal.status = "approved"
    goal.locked_at = datetime.utcnow()
    goal.manager_comment = form.comment.data
    db.session.commit()

    AuditService.log(
        "GOAL_APPROVED",
        "goal",
        goal.id,
        current_user.id,
        new_value={"status": "approved"},
        ip_address=request.remote_addr,
    )
    flash(f"Goal '{goal.title}' approved and locked.", "success")
    return redirect(url_for("manager.approvals"))


@manager_bp.route("/goals/<int:goal_id>/return", methods=["POST"])
@login_required
@role_required("manager")
def return_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    emp = User.query.get(goal.employee_id)
    if emp.manager_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("manager.approvals"))

    form = ReturnForm()
    if form.validate_on_submit():
        goal.status = "rework"
        goal.manager_comment = form.comment.data
        db.session.commit()
        AuditService.log(
            "GOAL_RETURNED",
            "goal",
            goal.id,
            current_user.id,
            new_value={"comment": form.comment.data},
            ip_address=request.remote_addr,
        )
        flash("Goal returned for rework.", "info")
    return redirect(url_for("manager.approvals"))


@manager_bp.route("/checkin/<int:employee_id>", methods=["GET", "POST"])
@login_required
@role_required("manager")
def checkin(employee_id):
    emp = User.query.get_or_404(employee_id)
    if emp.manager_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("manager.dashboard"))

    quarter = request.args.get("quarter", "Q1")
    goals = Goal.query.filter_by(
        employee_id=emp.id, status="approved"
    ).all()

    form = CheckinForm()
    if form.validate_on_submit():
        for goal in goals:
            ach = Achievement.query.filter_by(
                goal_id=goal.id, quarter=quarter
            ).first()
            if ach:
                ach.manager_comment = form.comment.data
                ach.checkin_at = datetime.utcnow()
        db.session.commit()
        AuditService.log(
            "CHECKIN_COMPLETED",
            "user",
            emp.id,
            current_user.id,
            new_value={"quarter": quarter},
            ip_address=request.remote_addr,
        )
        flash("Check-in saved.", "success")
        return redirect(url_for("manager.team_goals"))

    goals_data = []
    for g in goals:
        ach = Achievement.query.filter_by(goal_id=g.id, quarter=quarter).first()
        goals_data.append(
            {
                "goal": g,
                "achievement": ach,
                "title": g.title,
                "target": g.target,
                "actual": ach.actual_value if ach else "—",
                "status": ach.status if ach else "not_started",
            }
        )

    return render_template(
        "manager/checkin.html",
        employee=emp,
        goals_data=goals_data,
        form=form,
        quarter=quarter,
    )


@manager_bp.route("/api/ai-checkin-summary/<int:employee_id>")
@login_required
@role_required("manager")
def ai_checkin_summary(employee_id):
    emp = User.query.get_or_404(employee_id)
    quarter = request.args.get("quarter", "Q1")
    goals = Goal.query.filter_by(employee_id=emp.id, status="approved").all()
    summary = []
    for g in goals:
        ach = Achievement.query.filter_by(goal_id=g.id, quarter=quarter).first()
        summary.append(
            {
                "title": g.title,
                "target": g.target,
                "actual": ach.actual_value if ach else 0,
                "status": ach.status if ach else "not_started",
            }
        )
    comment = AIService.generate_checkin_comment(emp.name, summary)
    return jsonify({"comment": comment})
