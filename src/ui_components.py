"""UI styling, visualization components, and custom charts for IntelliGrade."""

import html
from typing import List, Tuple
import plotly.graph_objects as go
from src.models import (
    BLOOMS_COLORS,
    BLOOMS_DESCRIPTIONS,
    BLOOMS_ORDER,
    BloomsLevel,
    QuestionEvaluation,
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header styling */
.main-title {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem !important;
}

.subtitle-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.12);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 1.2rem;
}

/* Glassmorphic card styling */
.pedagogy-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.12);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pedagogy-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.2);
}

.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.card-content {
    font-size: 0.95rem;
    line-height: 1.6;
    color: inherit;
}

/* Tag Pills */
.tag-pill {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.verb-pill {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.keyword-pill {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.4);
}

/* Bloom's step hierarchy */
.blooms-tier-bar {
    display: flex;
    width: 100%;
    margin: 1rem 0 1.5rem 0;
    border-radius: 8px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.blooms-tier-step {
    flex: 1;
    text-align: center;
    padding: 0.6rem 0.2rem;
    font-size: 0.8rem;
    font-weight: 600;
    position: relative;
    transition: all 0.3s ease;
    opacity: 0.35;
}

.blooms-tier-step.active {
    opacity: 1.0;
    color: #ffffff !important;
    font-weight: 700;
    box-shadow: inset 0 -3px 0 #ffffff;
}

/* Status banner */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
}
.status-online {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.4);
}
.status-mock {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

/* Elevator suggestion box */
.elevator-card {
    border-left: 4px solid #8b5cf6;
    background: rgba(139, 92, 246, 0.08);
    padding: 0.9rem;
    border-radius: 8px;
    margin-top: 0.6rem;
}
</style>
"""


def render_difficulty_gauge(score: float) -> go.Figure:
    """Render high-polish speedometer gauge for difficulty score (1-10)."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            number={"suffix": "/10", "font": {"size": 36, "family": "Inter, sans-serif"}},
            title={"text": "Difficulty Index", "font": {"size": 16, "family": "Inter, sans-serif"}},
            gauge={
                "axis": {"range": [1.0, 10.0], "tickwidth": 1, "tickcolor": "#888"},
                "bar": {"color": "#6366f1", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 1,
                "bordercolor": "rgba(255,255,255,0.15)",
                "steps": [
                    {"range": [1.0, 3.0], "color": "rgba(59, 130, 246, 0.25)"},
                    {"range": [3.0, 6.0], "color": "rgba(16, 185, 129, 0.25)"},
                    {"range": [6.0, 8.5], "color": "rgba(245, 158, 11, 0.25)"},
                    {"range": [8.5, 10.0], "color": "rgba(239, 68, 68, 0.25)"},
                ],
                "threshold": {
                    "line": {"color": "#ec4899", "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )

    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=35, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "inherit"},
    )
    return fig


def render_blooms_hierarchy_html(current_level: BloomsLevel) -> str:
    """Render horizontal cognitive hierarchy step-bar with the active level highlighted."""
    steps_html = []
    for level in BLOOMS_ORDER:
        color = BLOOMS_COLORS[level]
        is_active = level == current_level
        active_cls = "active" if is_active else ""
        bg_style = f"background: {color};" if is_active else "background: rgba(255,255,255,0.04);"
        border_style = f"border-bottom: 3px solid {color};" if is_active else ""
        steps_html.append(
            f'<div class="blooms-tier-step {active_cls}" style="{bg_style} {border_style}">'
            f'{level.value.upper()}'
            f'</div>'
        )

    return f'<div class="blooms-tier-bar">{"".join(steps_html)}</div>'


def render_distribution_chart(evaluations: List[QuestionEvaluation]) -> go.Figure:
    """Render interactive Donut Chart for Bloom's Taxonomy distribution in batch evaluation."""
    counts = {level.value: 0 for level in BLOOMS_ORDER}
    for ev in evaluations:
        lvl_val = ev.blooms_level.value if hasattr(ev.blooms_level, "value") else str(ev.blooms_level)
        counts[lvl_val] = counts.get(lvl_val, 0) + 1

    labels = [k for k, v in counts.items() if v > 0]
    values = [v for k, v in counts.items() if v > 0]
    colors = [BLOOMS_COLORS[BloomsLevel(lbl)] for lbl in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
            )
        ]
    )
    fig.update_layout(
        title="Cognitive Tier Distribution (Bloom's)",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def render_difficulty_histogram(evaluations: List[QuestionEvaluation]) -> go.Figure:
    """Render histogram/bar of difficulty scores in batch evaluation."""
    scores = [ev.difficulty_score for ev in evaluations]

    fig = go.Figure(
        data=[
            go.Histogram(
                x=scores,
                xbins=dict(start=1.0, end=10.0, size=1.0),
                marker_color="#8b5cf6",
                opacity=0.85,
            )
        ]
    )
    fig.update_layout(
        title="Difficulty Score Spread (1 - 10)",
        xaxis_title="Difficulty Score",
        yaxis_title="Question Count",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_cognitive_radar(evaluations: List[QuestionEvaluation]) -> go.Figure:
    """Render 6-axis Radar / Spider chart representing exam paper cognitive coverage."""
    counts = {level.value: 0 for level in BLOOMS_ORDER}
    for ev in evaluations:
        lvl_val = ev.blooms_level.value if hasattr(ev.blooms_level, "value") else str(ev.blooms_level)
        counts[lvl_val] = counts.get(lvl_val, 0) + 1

    total = max(1, len(evaluations))
    percentages = [(counts[level.value] / total) * 100 for level in BLOOMS_ORDER]
    categories = [level.value for level in BLOOMS_ORDER]

    # Close the polygon by repeating first item
    r_vals = percentages + [percentages[0]]
    theta_vals = categories + [categories[0]]

    # Ideal recommended benchmark distribution (20% Rem, 20% Und, 25% App, 15% Ana, 10% Eva, 10% Cre)
    ideal_pct = [20, 20, 25, 15, 10, 10]
    ideal_r = ideal_pct + [ideal_pct[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=ideal_r,
            theta=theta_vals,
            fill="toself",
            name="Pedagogical Benchmark",
            line=dict(color="rgba(156, 163, 175, 0.6)", dash="dash"),
            fillcolor="rgba(156, 163, 175, 0.1)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=r_vals,
            theta=theta_vals,
            fill="toself",
            name="This Examination Paper",
            line=dict(color="#3b82f6", width=2.5),
            fillcolor="rgba(59, 130, 246, 0.35)",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(50, max(percentages) + 10)]),
        ),
        title="Cognitive Radar Profile vs Pedagogical Benchmark",
        height=340,
        margin=dict(l=30, r=30, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
    )
    return fig


def compute_exam_balance_health(
    evaluations: List[QuestionEvaluation],
) -> Tuple[int, str, str, str]:
    """
    Calculate Exam Balance Health Index (0-100%).
    Returns: (score, status_label, badge_color, feedback_critique)
    """
    if not evaluations:
        return 0, "No Questions", "#888888", "Upload or paste questions to calculate balance."

    total = len(evaluations)
    counts = {level: 0 for level in BLOOMS_ORDER}
    for ev in evaluations:
        counts[ev.blooms_level] = counts.get(ev.blooms_level, 0) + 1

    lower_order = (counts[BloomsLevel.REMEMBER] + counts[BloomsLevel.UNDERSTAND]) / total
    procedural = counts[BloomsLevel.APPLY] / total
    higher_order = (
        counts[BloomsLevel.ANALYZE] + counts[BloomsLevel.EVALUATE] + counts[BloomsLevel.CREATE]
    ) / total

    # Scoring algorithm based on balanced curricular distribution
    # Ideal: ~25-35% lower order, ~30-40% procedural, ~30-45% higher order
    score = 100

    # Penalties
    if lower_order > 0.65:
        penalty = (lower_order - 0.65) * 80
        score -= penalty
        critique = (
            f"Over-indexed on rote recall ({int(lower_order*100)}% Remember/Understand). "
            "Incorporate more analytical or design questions to evaluate deeper mastery."
        )
        status = "Rote Recall Skewed"
        color = "#ef4444"
    elif higher_order < 0.15:
        score -= 25
        critique = (
            "Insufficient higher-order thinking (only "
            f"{int(higher_order*100)}% Analyze/Evaluate/Create). Add questions requiring critique or synthesis."
        )
        status = "Deficient Critical Depth"
        color = "#f59e0b"
    elif procedural < 0.10 and total >= 5:
        score -= 15
        critique = (
            "Low procedural application component. Consider adding practical calculation or execution problems."
        )
        status = "Low Procedural Weight"
        color = "#f59e0b"
    else:
        critique = (
            "Well-balanced distribution across foundational recall, procedural problem solving, "
            "and higher-order cognitive analysis."
        )
        status = "Optimal Pedagogical Balance"
        color = "#10b981"

    final_score = int(max(20, min(100, score)))
    return final_score, status, color, critique


def generate_html_dossier(
    evaluations: List[QuestionEvaluation], course_title: str = "Examination Assessment"
) -> str:
    """Generate standalone, print-ready HTML executive quality assurance dossier."""
    score, status, color, critique = compute_exam_balance_health(evaluations)
    diffs = [e.difficulty_score for e in evaluations]
    avg_diff = round(sum(diffs) / len(diffs), 1) if diffs else 0.0

    rows_html = []
    for idx, e in enumerate(evaluations, 1):
        c = BLOOMS_COLORS[e.blooms_level]
        rows_html.append(
            f"""
            <tr>
                <td style="text-align: center; font-weight: bold;">{idx}</td>
                <td>{html.escape(e.question)}</td>
                <td style="text-align: center;">
                    <span style="background: {c}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                        L{e.blooms_level_index}: {e.blooms_level.value}
                    </span>
                </td>
                <td style="text-align: center; font-weight: bold;">{e.difficulty_score}/10</td>
                <td style="font-size: 12px;">{html.escape(e.pedagogical_reasoning)}</td>
                <td style="font-size: 12px; color: #166534;">{html.escape(e.improvement_suggestions)}</td>
            </tr>
            """
        )

    table_body = "".join(rows_html)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>IntelliGrade Pedagogical Audit Dossier</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #1f2937; background: #ffffff; }}
.header {{ border-bottom: 3px solid #3b82f6; padding-bottom: 15px; margin-bottom: 25px; }}
h1 {{ color: #1e3a8a; margin: 0 0 5px 0; font-size: 24px; }}
.subtitle {{ color: #6b7280; font-size: 14px; margin: 0; }}
.metric-grid {{ display: flex; gap: 20px; margin-bottom: 25px; }}
.metric-card {{ flex: 1; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; text-align: center; }}
.metric-val {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
.metric-lbl {{ font-size: 12px; color: #6b7280; text-transform: uppercase; margin-top: 5px; }}
.balance-box {{ background: #eff6ff; border-left: 5px solid {color}; padding: 15px; border-radius: 4px; margin-bottom: 25px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
th {{ background: #1e40af; color: white; text-align: left; padding: 10px; font-size: 12px; }}
td {{ padding: 10px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
tr:nth-child(even) {{ background: #f9fafb; }}
.footer {{ margin-top: 40px; border-top: 1px solid #e5e7eb; padding-top: 20px; display: flex; justify-content: space-between; font-size: 11px; color: #9ca3af; }}
.sign-box {{ margin-top: 30px; border-top: 1px dashed #6b7280; width: 220px; text-align: center; padding-top: 5px; font-size: 12px; }}
</style>
</head>
<body>
<div class="header">
    <h1>IntelliGrade Pedagogical Audit Dossier</h1>
    <p class="subtitle">Air-Gapped Academic Quality Assurance & Revised Bloom's Taxonomy Verification</p>
    <p style="font-size: 12px; color: #4b5563; margin-top: 5px;">Document Subject: <strong>{html.escape(course_title)}</strong> | Security Tier: <strong>Confidential / On-Premise LAN</strong></p>
</div>

<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-val">{len(evaluations)}</div>
        <div class="metric-lbl">Total Questions Audited</div>
    </div>
    <div class="metric-card">
        <div class="metric-val">{avg_diff} / 10</div>
        <div class="metric-lbl">Mean Difficulty Score</div>
    </div>
    <div class="metric-card">
        <div class="metric-val" style="color: {color};">{score}%</div>
        <div class="metric-lbl">Exam Balance Index</div>
    </div>
    <div class="metric-card">
        <div class="metric-val" style="font-size: 18px; color: {color};">{status}</div>
        <div class="metric-lbl">Curricular Alignment</div>
    </div>
</div>

<div class="balance-box">
    <strong>Pedagogical Committee Assessment:</strong><br/>
    {critique}
</div>

<h2>Audited Question Inventory</h2>
<table>
    <thead>
        <tr>
            <th style="width: 40px; text-align: center;">#</th>
            <th style="width: 30%;">Question Text</th>
            <th style="width: 14%; text-align: center;">Bloom's Level</th>
            <th style="width: 10%; text-align: center;">Difficulty</th>
            <th style="width: 23%;">Pedagogical Reasoning</th>
            <th style="width: 23%;">Improvement Suggestion</th>
        </tr>
    </thead>
    <tbody>
        {table_body}
    </tbody>
</table>

<div style="margin-top: 40px; display: flex; justify-content: space-between;">
    <div>
        <div class="sign-box">Academic Auditor Signature</div>
    </div>
    <div>
        <div class="sign-box">Department Chair Signature</div>
    </div>
</div>

<div class="footer">
    <div>Generated autonomously by IntelliGrade Air-Gapped Classifier</div>
    <div>Strict Compliance: Zero Cloud Telemetry Guaranteed</div>
</div>
</body>
</html>
"""
