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
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from app.extensions import db
from app.models.goal import Goal
from app.models.achievement import Achievement
from app.utils.decorators import role_required
from app.utils.validators import sanitize_text
from app.services.goal_service import GoalService
from app.services.audit_service import AuditService

employee_bp = Blueprint("employee", __name__, url_prefix="/employee")

THRUST_AREAS = [
    ("Revenue Growth", "Revenue Growth"),
    ("Customer Experience", "Customer Experience"),
    ("Operational Excellence", "Operational Excellence"),
    ("Innovation", "Innovation"),
    ("People & Culture", "People & Culture"),
]

UOM_CHOICES = [
    ("numeric_min", "Numeric — Higher is better"),
    ("numeric_max", "Numeric — Lower is better"),
    ("timeline", "Timeline / Date-based"),
    ("zero", "Zero-based (0 = success)"),
]


class GoalForm(FlaskForm):
    thrust_area = SelectField("Thrust Area", choices=THRUST_AREAS, validators=[DataRequired()])
    title = StringField("Goal Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    uom_type = SelectField("Unit of Measurement", choices=UOM_CHOICES, validators=[DataRequired()])
    target = FloatField("Target", validators=[DataRequired(), NumberRange(min=0)])
    weightage = FloatField(
        "Weightage (%)",
        validators=[DataRequired(), NumberRange(min=10, max=100)],
    )
    submit = SubmitField("Save Goal")


class AchievementForm(FlaskForm):
    actual_value = FloatField("Actual Achievement", validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[
            ("not_started", "Not Started"),
            ("on_track", "On Track"),
            ("completed", "Completed"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Achievement")


@employee_bp.route("/dashboard")
@login_required
@role_required("employee")
def dashboard():
    stats = GoalService.get_employee_stats(current_user.id)
    goals = Goal.query.filter_by(
        employee_id=current_user.id,
        cycle_year=current_app.config["CYCLE_YEAR"],
    ).order_by(Goal.created_at.desc()).all()
    progress = GoalService.get_quarter_progress(current_user.id, "Q1")
    from app.models.cycle_config import CycleConfig
    q1 = CycleConfig.query.filter_by(phase="Q1").first()
    chart_labels = [e["title"] for e in progress["entries"]]
    chart_scores = [e["score"] for e in progress["entries"]]
    return render_template(
        "employee/dashboard.html",
        stats=stats,
        goals=goals,
        progress=progress,
        cycle_phase=q1,
        chart_labels=chart_labels,
        chart_scores=chart_scores,
    )


@employee_bp.route("/goals")
@login_required
@role_required("employee")
def goal_list():
    goals = Goal.query.filter_by(
        employee_id=current_user.id,
        cycle_year=current_app.config["CYCLE_YEAR"],
    ).order_by(Goal.created_at.desc()).all()
    weightage_used = sum(g.weightage for g in goals)
    return render_template(
        "employee/goal_list.html", goals=goals, weightage_used=weightage_used
    )


@employee_bp.route("/goals/create", methods=["GET", "POST"])
@login_required
@role_required("employee")
def goal_create():
    can_add, msg = GoalService.can_add_goal(current_user.id)
    if not can_add:
        flash(msg, "warning")
        return redirect(url_for("employee.goal_list"))

    form = GoalForm()
    existing_total = GoalService.total_weightage(current_user.id)
    remaining = GoalService.remaining_weightage(current_user.id)

    if form.validate_on_submit():
        weightage = float(form.weightage.data)
        errors, _ = GoalService.validate_weightage(current_user.id, weightage)
        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            goal = Goal(
                employee_id=current_user.id,
                thrust_area=form.thrust_area.data,
                title=sanitize_text(form.title.data, 200),
                description=sanitize_text(form.description.data),
                uom_type=form.uom_type.data,
                target=form.target.data,
                weightage=weightage,
                status="draft",
                cycle_year=current_app.config["CYCLE_YEAR"],
            )
            db.session.add(goal)
            db.session.commit()
            AuditService.log(
                "GOAL_CREATED",
                "goal",
                goal.id,
                current_user.id,
                new_value={"title": goal.title},
                ip_address=request.remote_addr,
            )
            flash("Goal saved as draft.", "success")
            return redirect(url_for("employee.goal_list"))
    elif request.method == "POST":
        flash("Please fix the errors below.", "danger")

    return render_template(
        "employee/goal_create.html",
        form=form,
        existing_total=existing_total,
        remaining=remaining,
        edit_mode=False,
    )


@employee_bp.route("/goals/<int:goal_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("employee")
def goal_edit(goal_id):
    goal = Goal.query.filter_by(
        id=goal_id, employee_id=current_user.id
    ).first_or_404()

    if not goal.is_editable:
        flash("This goal cannot be edited.", "warning")
        return redirect(url_for("employee.goal_list"))

    form = GoalForm(obj=goal)
    if goal.shared_from_id:
        form.title.render_kw = {"readonly": True}
        form.target.render_kw = {"readonly": True}

    if form.validate_on_submit():
        errors, _ = GoalService.validate_weightage(
            current_user.id, form.weightage.data, exclude_goal_id=goal.id
        )
        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            old = {"title": goal.title, "weightage": goal.weightage}
            if not goal.shared_from_id:
                goal.title = sanitize_text(form.title.data, 200)
                goal.description = sanitize_text(form.description.data)
                goal.uom_type = form.uom_type.data
                goal.target = form.target.data
                goal.thrust_area = form.thrust_area.data
            goal.weightage = form.weightage.data
            goal.updated_at = datetime.utcnow()
            db.session.commit()
            AuditService.log(
                "GOAL_EDITED",
                "goal",
                goal.id,
                current_user.id,
                old_value=old,
                new_value={"title": goal.title, "weightage": goal.weightage},
                ip_address=request.remote_addr,
            )
            flash("Goal updated.", "success")
            return redirect(url_for("employee.goal_list"))

    existing_total = GoalService.total_weightage(
        current_user.id, exclude_goal_id=goal.id
    )
    remaining = GoalService.remaining_weightage(
        current_user.id, exclude_goal_id=goal.id
    )
    return render_template(
        "employee/goal_create.html",
        form=form,
        goal=goal,
        existing_total=existing_total,
        remaining=remaining,
        edit_mode=True,
    )


@employee_bp.route("/goals/<int:goal_id>/submit", methods=["POST"])
@login_required
@role_required("employee")
def goal_submit(goal_id):
    goal = Goal.query.filter_by(
        id=goal_id, employee_id=current_user.id
    ).first_or_404()
    if goal.status not in ("draft", "rework"):
        flash("Goal cannot be submitted in current status.", "warning")
        return redirect(url_for("employee.goal_list"))

    goal.status = "submitted"
    goal.updated_at = datetime.utcnow()
    db.session.commit()
    AuditService.log(
        "GOAL_SUBMITTED",
        "goal",
        goal.id,
        current_user.id,
        ip_address=request.remote_addr,
    )
    flash("Goal submitted for manager approval.", "success")
    return redirect(url_for("employee.goal_list"))


@employee_bp.route("/achievement/<int:goal_id>", methods=["GET", "POST"])
@login_required
@role_required("employee")
def achievement(goal_id):
    goal = Goal.query.filter_by(
        id=goal_id, employee_id=current_user.id
    ).first_or_404()

    if goal.status not in ("approved", "locked"):
        flash("Achievements can only be logged for approved goals.", "warning")
        return redirect(url_for("employee.dashboard"))

    quarter = request.args.get("quarter", "Q1")
    ach = Achievement.query.filter_by(goal_id=goal.id, quarter=quarter).first()
    if not ach:
        ach = Achievement(goal_id=goal.id, quarter=quarter)
        db.session.add(ach)

    form = AchievementForm(obj=ach)
    if form.validate_on_submit():
        ach.actual_value = form.actual_value.data
        ach.status = form.status.data
        ach.submitted_at = datetime.utcnow()
        ach.compute_progress_score()
        db.session.commit()
        AuditService.log(
            "ACHIEVEMENT_UPDATED",
            "achievement",
            ach.id,
            current_user.id,
            new_value={"quarter": quarter, "actual": ach.actual_value},
            ip_address=request.remote_addr,
        )
        flash(f"{quarter} achievement saved.", "success")
        return redirect(url_for("employee.dashboard"))

    return render_template(
        "employee/achievement.html",
        form=form,
        goal=goal,
        quarter=quarter,
        achievement=ach,
    )
