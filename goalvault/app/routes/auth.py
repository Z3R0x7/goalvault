from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from app.extensions import db, limiter
from app.models.user import User
from app.services.audit_service import AuditService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(_role_dashboard(current_user.role))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if not user or not user.is_active:
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if user.failed_logins >= 5:
            flash("Account locked due to too many failed attempts. Contact admin.", "danger")
            AuditService.log(
                "LOGIN_LOCKED",
                "user",
                user.id,
                user.id,
                ip_address=request.remote_addr,
            )
            return render_template("auth/login.html", form=form)

        if not user.check_password(form.password.data):
            user.failed_logins = (user.failed_logins or 0) + 1
            db.session.commit()
            AuditService.log(
                "LOGIN_FAILED",
                "user",
                user.id,
                user.id,
                {"failed_count": user.failed_logins},
                ip_address=request.remote_addr,
            )
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        user.failed_logins = 0
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        AuditService.log(
            "LOGIN_SUCCESS",
            "user",
            user.id,
            user.id,
            ip_address=request.remote_addr,
        )
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(_role_dashboard(user.role))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    AuditService.log(
        "LOGOUT",
        "user",
        current_user.id,
        current_user.id,
        ip_address=request.remote_addr,
    )
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


def _role_dashboard(role):
    return {
        "employee": url_for("employee.dashboard"),
        "manager": url_for("manager.dashboard"),
        "admin": url_for("admin.dashboard"),
    }.get(role, url_for("auth.login"))
