import os
import json
import re
import requests
from flask import current_app

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-70b-versatile"


class AIService:
    @staticmethod
    def _headers():
        key = current_app.config.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY", "")
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _has_api_key():
        key = current_app.config.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY", "")
        return bool(key and key.strip())

    @staticmethod
    def _parse_json_response(content):
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n?", "", content)
            content = re.sub(r"\n?```$", "", content)
        return json.loads(content)

    @staticmethod
    def _demo_goal_analysis(title, description, uom_type, target):
        return {
            "quality_score": 7,
            "is_smart": True,
            "issues": [],
            "suggestions": [
                "Add a specific deadline or milestone for quarterly tracking.",
                "Quantify success criteria more explicitly in the description.",
                "Align the target with your team's annual OKR where possible.",
            ],
            "uom_appropriate": True,
            "uom_comment": f"The selected UoM ({uom_type}) fits this type of goal.",
            "demo_mode": True,
        }

    @staticmethod
    def analyse_goal(title: str, description: str, uom_type: str, target: float) -> dict:
        if not AIService._has_api_key():
            return AIService._demo_goal_analysis(title, description, uom_type, target)

        prompt = f"""You are a professional performance management consultant reviewing an employee goal.

Goal Title: {title}
Description: {description}
Unit of Measurement: {uom_type}
Target: {target}

Analyse this goal and respond ONLY with valid JSON in this exact format:
{{
    "quality_score": <integer 1-10>,
    "is_smart": <true/false>,
    "issues": [<list of specific issues, max 3>],
    "suggestions": [<list of concrete improvements, max 3>],
    "uom_appropriate": <true/false>,
    "uom_comment": "<one sentence on UoM fit>"
}}
No preamble. No markdown. Only the JSON object."""

        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 400,
        }
        try:
            r = requests.post(
                GROQ_API_URL, headers=AIService._headers(), json=payload, timeout=15
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            return AIService._parse_json_response(content)
        except Exception as e:
            return {
                "error": str(e),
                "quality_score": 0,
                "issues": ["AI service unavailable. Add GROQ_API_KEY to .env"],
                "suggestions": [],
                "uom_appropriate": True,
                "uom_comment": "",
            }

    @staticmethod
    def generate_checkin_comment(employee_name: str, goals_summary: list) -> str:
        if not AIService._has_api_key():
            lines = [
                f"Quarterly check-in summary for {employee_name}:",
                "Overall progress is on track across submitted goals.",
            ]
            for g in goals_summary:
                lines.append(
                    f"- {g['title']}: planned {g['target']}, achieved {g['actual']} ({g['status']})."
                )
            lines.append(
                "Recommend continuing focus on lagging items next quarter. (Demo mode — add GROQ_API_KEY for live AI.)"
            )
            return " ".join(lines)

        goals_text = "\n".join(
            [
                f"- {g['title']}: Planned {g['target']}, Achieved {g['actual']}, Status: {g['status']}"
                for g in goals_summary
            ]
        )
        prompt = f"""Write a professional, concise quarterly check-in comment for {employee_name}'s performance review.

Goals progress:
{goals_text}

Write 3-4 sentences that acknowledge achievements, note areas needing attention, and suggest a next step.
Keep it factual and constructive. Plain text only, no bullet points."""

        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 200,
        }
        try:
            r = requests.post(
                GROQ_API_URL, headers=AIService._headers(), json=payload, timeout=15
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            return "Unable to generate summary. Please write manually."
