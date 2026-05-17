from flask import Blueprint, request, jsonify, send_file, current_app
from app.extensions import csrf
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.ai_service import AIService
from app.services.audit_service import AuditService
from app.services.export_service import ExportService
from app.services.analytics_service import AnalyticsService

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/ai/analyse-goal", methods=["POST"])
@csrf.exempt
@login_required
def analyse_goal():
    data = request.get_json() or {}
    result = AIService.analyse_goal(
        title=data.get("title", ""),
        description=data.get("description", ""),
        uom_type=data.get("uom_type", "numeric_min"),
        target=float(data.get("target") or 0),
    )
    return jsonify(result)


@api_bp.route("/audit/verify")
@login_required
@role_required("admin")
def verify_audit():
    result = AuditService.verify_chain()
    return jsonify(result)


@api_bp.route("/analytics/summary")
@login_required
@role_required("admin")
def analytics_summary():
    year = request.args.get("year", current_app.config.get("CYCLE_YEAR", 2025), type=int)
    return jsonify(AnalyticsService.get_org_summary(year))


@api_bp.route("/export/achievement-report")
@login_required
@role_required("admin")
def export_report():
    year = request.args.get("year", current_app.config.get("CYCLE_YEAR", 2025), type=int)
    output, filename = ExportService.generate_achievement_report(year)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
