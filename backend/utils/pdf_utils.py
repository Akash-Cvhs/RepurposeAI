from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import html
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.config import PDF_LAYOUT_MODE, REPORTS_DIR


def _render_footer(canvas, doc, metadata: dict[str, str] | None = None):
    if canvas.getPageNumber() == 1 and metadata:
        canvas.setTitle(metadata.get("title", "MoleculeIQ Innovation Product Story"))
        canvas.setAuthor(metadata.get("author", "MoleculeIQ"))
        canvas.setSubject(metadata.get("subject", "Drug Repurposing Intelligence Report"))
        canvas.setCreator(metadata.get("creator", "MoleculeIQ Agentic Pipeline"))
        canvas.setKeywords(metadata.get("keywords", "drug repurposing, innovation, clinical trials, patents"))

    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(18 * mm, 12 * mm, "MoleculeIQ Innovation Report")
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 12 * mm, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def _truncate(value: Any, max_len: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _safe_text(value: Any) -> str:
    """Escape paragraph text to avoid ReportLab XML parsing glitches."""
    return html.escape(str(value or "").strip(), quote=False)


def _add_bullets(story: list[Any], items: list[str], style) -> None:
    if not items:
        story.append(Paragraph("&bull; Not available", style))
        return
    for item in items:
        story.append(Paragraph(f"&bull; {_safe_text(_truncate(item, 200))}", style))


def _add_table(story: list[Any], headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
    data: list[list[Any]] = []
    data.append([Paragraph(f"<b>{_safe_text(h)}</b>", _table_body_style) for h in headers])
    source_rows = rows if rows else [["-"] * len(headers)]
    for row in source_rows:
        data.append([Paragraph(_safe_text(_truncate(cell, 160)), _table_body_style) for cell in row])

    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1B365D")),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(table)


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)]+", text)


_table_body_style = getSampleStyleSheet()["BodyText"]
_table_body_style.fontName = "Helvetica"
_table_body_style.fontSize = 8.4
_table_body_style.leading = 10.5

_reference_style = getSampleStyleSheet()["BodyText"]
_reference_style.fontName = "Helvetica"
_reference_style.fontSize = 9
_reference_style.leading = 10


def _layout_mode(mode: str | None = None) -> str:
    chosen = (mode or PDF_LAYOUT_MODE).strip().lower()
    return chosen if chosen in {"dense", "presentation"} else "dense"


def _layout_params(mode: str) -> dict[str, Any]:
    if mode == "presentation":
        return {
            "cover_top_spacer": 56,
            "section_spacer": 9,
            "sub_spacer": 7,
            "max_trials": 8,
            "max_patents": 8,
            "max_refs": 16,
        }
    return {
        "cover_top_spacer": 34,
        "section_spacer": 6,
        "sub_spacer": 4,
        "max_trials": 6,
        "max_patents": 6,
        "max_refs": 12,
    }


def _risk_badge_chip(risk_value: str) -> Table:
    risk = (risk_value or "unknown").strip().lower()
    if risk == "low":
        bg = colors.HexColor("#DDF4E5")
        fg = colors.HexColor("#1F6B3A")
    elif risk == "medium":
        bg = colors.HexColor("#FFF1D6")
        fg = colors.HexColor("#8A5A00")
    elif risk == "high":
        bg = colors.HexColor("#FDE2E1")
        fg = colors.HexColor("#9D1D1D")
    else:
        bg = colors.HexColor("#E9ECEF")
        fg = colors.HexColor("#495057")

    value = Paragraph(f"<b>{_safe_text(risk.upper())}</b>", _table_body_style)
    chip = Table([[value]], colWidths=[28 * mm], rowHeights=[7 * mm])
    chip.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("TEXTCOLOR", (0, 0), (-1, -1), fg),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#C4CFDD")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return chip


def _build_report(story: list[Any], styles, data: dict[str, Any]) -> None:
    title = styles["Title"]
    heading = styles["Heading2"]
    body = styles["BodyText"]

    molecule = str(data.get("molecule", "unknown"))
    indication = str(data.get("indication", "unknown"))
    query = str(data.get("query", "")).strip()
    trials = data.get("trials", []) or []
    patents = data.get("patents", []) or []
    web = data.get("web_findings", []) or []
    fto = str(data.get("fto_risk", "unknown"))
    risk_assumptions = data.get("risk_assumptions", []) or []
    template = data.get("template", {}) if isinstance(data.get("template", {}), dict) else {}
    mode = _layout_mode(data.get("pdf_layout_mode") if isinstance(data, dict) else None)
    layout = _layout_params(mode)

    unmet_bullets = template.get("unmet_need_bullets")
    if not isinstance(unmet_bullets, list) or not unmet_bullets:
        unmet_bullets = [
            f"{indication} remains a high-burden condition with heterogeneous response to standard care.",
            "Recurrence and resistance patterns still drive unmet clinical needs.",
            "Adjunct, cost-effective repositioning strategies can improve time-to-impact.",
        ]

    signal = "Low"
    if trials:
        signal = "Moderate"
    if len(trials) >= 2 and fto.lower() != "high":
        signal = "High"

    # Cover
    story.append(Spacer(1, layout["cover_top_spacer"]))
    story.append(Paragraph(str(template.get("title") or "Innovation Product Story"), title))
    story.append(Spacer(1, layout["section_spacer"]))
    subtitle = str(template.get("subtitle") or "{molecule} for {indication}")
    subtitle = subtitle.replace("{molecule}", molecule).replace("{indication}", indication)
    subtitle = subtitle.replace("{molecule_title}", molecule.title()).replace("{indication_title}", indication.title())
    story.append(Paragraph(subtitle, heading))
    story.append(Spacer(1, layout["section_spacer"]))
    story.append(Paragraph(f"Query: {_truncate(query, 240)}", body))
    story.append(Paragraph(f"Generated: {datetime.now(timezone.utc).isoformat()}", body))
    story.append(PageBreak())

    # Executive summary
    story.append(Paragraph("Executive Summary", heading))
    _add_bullets(
        story,
        [
            f"Repurposing assessment for {molecule} in {indication}.",
            "Clinical, patent, and scientific evidence synthesized in one view.",
            f"Overall signal: {signal} potential.",
        ],
        body,
    )
    story.append(Spacer(1, layout["section_spacer"]))

    # Key highlights
    story.append(Paragraph("Key Highlights", heading))
    _add_table(
        story,
        ["Metric", "Value"],
        [
            ["Opportunity Signal", signal],
            ["FTO Risk", fto],
            ["Trials Available", str(len(trials))],
            ["Patents Considered", str(len(patents))],
        ],
        [80 * mm, 90 * mm],
    )
    story.append(Spacer(1, layout["section_spacer"]))

    story.append(Paragraph("Risk Badge", heading))
    story.append(_risk_badge_chip(fto))
    story.append(Spacer(1, layout["sub_spacer"]))

    # Context + unmet need
    story.append(Paragraph("1. Context & Query", heading))
    story.append(Paragraph(f"Molecule: {molecule}", body))
    story.append(Paragraph(f"Indication: {indication}", body))
    story.append(Paragraph("Objective: Evaluate repurposing potential and innovation feasibility", body))
    story.append(Spacer(1, layout["sub_spacer"]))

    story.append(Paragraph("2. Unmet Medical Need", heading))
    _add_bullets(story, [str(x) for x in unmet_bullets], body)
    story.append(Spacer(1, layout["section_spacer"]))

    # Clinical
    story.append(Paragraph("3. Clinical Trial Landscape", heading))
    _add_table(
        story,
        ["Metric", "Value"],
        [
            ["Trial count", str(len(trials))],
            ["Recruiting/Active signal", "Yes" if len(trials) > 0 else "No"],
            ["Evidence maturity", "Emerging" if len(trials) <= 3 else "Growing"],
        ],
        [130 * mm, 50 * mm],
    )
    story.append(Spacer(1, layout["sub_spacer"]))
    trial_rows = [
        [
            _truncate(t.get("nct_id", ""), 20),
            _truncate(t.get("title", ""), 52),
            _truncate(t.get("phase", ""), 14),
            _truncate(t.get("status", ""), 15),
        ]
        for t in trials[: layout["max_trials"]]
    ]
    _add_table(story, ["NCT", "Title", "Phase", "Status"], trial_rows, [28 * mm, 90 * mm, 24 * mm, 36 * mm])
    if len(trials) > layout["max_trials"]:
        story.append(Paragraph(f"Showing top {layout['max_trials']} of {len(trials)} trials.", body))
    story.append(Spacer(1, layout["section_spacer"]))

    # Patent
    story.append(Paragraph("4. Patent Landscape & FTO", heading))
    story.append(Paragraph(f"Computed FTO risk: {fto}", body))
    patent_rows = [
        [
            _truncate(p.get("patent_id", ""), 24),
            _truncate(p.get("title", ""), 50),
            _truncate(p.get("jurisdiction", ""), 12),
            _truncate(p.get("expiry_date", ""), 16),
        ]
        for p in patents[: layout["max_patents"]]
    ]
    _add_table(story, ["Patent", "Title", "Region", "Expiry"], patent_rows, [34 * mm, 86 * mm, 24 * mm, 34 * mm])
    if len(patents) > layout["max_patents"]:
        story.append(Paragraph(f"Showing top {layout['max_patents']} of {len(patents)} patents.", body))
    story.append(Spacer(1, layout["section_spacer"]))

    # Scientific evidence
    story.append(Paragraph("5. Scientific Evidence", heading))
    web_list = web if isinstance(web, list) else [str(web)]
    _add_bullets(story, [str(x) for x in web_list], body)
    story.append(Spacer(1, layout["section_spacer"]))

    # Synthesis
    story.append(Paragraph("6. AI Synthesis", heading))
    _add_bullets(
        story,
        [
            f"Clinical signal: {'present' if trials else 'limited'}",
            f"Patent constraint: {fto}",
            f"Overall: {signal} opportunity",
        ],
        body,
    )
    story.append(Spacer(1, layout["section_spacer"]))

    # Opportunity + business impact
    story.append(Paragraph("7. Innovation Opportunity", heading))
    _add_bullets(
        story,
        [
            f"{molecule} may be explored as an adjunct strategy in {indication}.",
            "Prioritize cohort selection and combination rationale.",
            "Differentiate around claims and positioning strategy.",
        ],
        body,
    )
    story.append(Spacer(1, layout["section_spacer"]))

    story.append(Paragraph("8. Business Impact", heading))
    _add_bullets(
        story,
        [
            "Compresses discovery synthesis cycle from weeks to minutes.",
            "Supports high-throughput prioritization with transparent evidence trails.",
            "Improves decision quality by combining technical and commercial signals.",
        ],
        body,
    )
    story.append(Spacer(1, layout["section_spacer"]))

    # Risks + recommendation
    story.append(Paragraph("9. Risks & Assumptions", heading))
    _add_bullets(story, [str(x) for x in risk_assumptions], body)
    story.append(Spacer(1, layout["section_spacer"]))

    story.append(Paragraph("10. Final Recommendation", heading))
    _add_bullets(
        story,
        [
            "Proceed with focused clinical validation and legal review checkpoints.",
            "Stress-test commercialization routes against claim boundaries.",
            "Advance only if subgroup efficacy and risk profile remain favorable.",
        ],
        body,
    )
    story.append(Spacer(1, layout["section_spacer"]))

    story.append(Paragraph("11. Conclusion", heading))
    conclusion_line = str(
        template.get("conclusion_line")
        or "This report provides a practical, evidence-linked decision narrative for repurposing strategy design."
    )
    story.append(Paragraph(conclusion_line, body))
    story.append(Spacer(1, layout["section_spacer"]))

    # References
    story.append(Paragraph("References", heading))
    refs: list[str] = []
    for t in trials[:4]:
        nct_id = str(t.get("nct_id", "")).strip()
        if nct_id:
            refs.append(f"ClinicalTrials.gov - {nct_id}")
    for p in patents[:4]:
        patent_id = str(p.get("patent_id", "")).strip()
        if patent_id:
            refs.append(f"Patent - {patent_id}")
        patent_url = str(p.get("url", "")).strip()
        if patent_url:
            refs.append(patent_url)
    for finding in web_list[:2]:
        refs.append(_truncate(finding, 160))
        refs.extend(_extract_urls(str(finding)))

    # De-duplicate while preserving order.
    dedup_refs: list[str] = []
    seen: set[str] = set()
    for item in refs:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        dedup_refs.append(key)

    _add_bullets(story, dedup_refs[: layout["max_refs"]], _reference_style)


def create_report_pdf(markdown_text: str, filename_slug: str, report_data: dict[str, Any] | None = None) -> str:
    """Create a production-style PDF report from structured data or markdown fallback."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = REPORTS_DIR / f"{filename_slug}-{timestamp}.pdf"

    mode = _layout_mode(report_data.get("pdf_layout_mode") if isinstance(report_data, dict) else None)

    if mode == "presentation":
        left_margin = 20 * mm
        right_margin = 20 * mm
        top_margin = 18 * mm
        bottom_margin = 20 * mm
    else:
        left_margin = 16 * mm
        right_margin = 16 * mm
        top_margin = 14 * mm
        bottom_margin = 16 * mm

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    styles = getSampleStyleSheet()
    styles["Title"].fontName = "Helvetica-Bold"
    styles["Heading2"].fontName = "Helvetica-Bold"
    styles["BodyText"].fontName = "Helvetica"
    if mode == "presentation":
        styles["Title"].fontSize = 22
        styles["Title"].leading = 26
        styles["Heading2"].fontSize = 13
        styles["Heading2"].leading = 17
        styles["Heading2"].spaceBefore = 6
        styles["Heading2"].spaceAfter = 3
        styles["BodyText"].fontSize = 10.3
        styles["BodyText"].leading = 13.2
    else:
        styles["Title"].fontSize = 20
        styles["Title"].leading = 23
        styles["Heading2"].fontSize = 12
        styles["Heading2"].leading = 15
        styles["Heading2"].spaceBefore = 4
        styles["Heading2"].spaceAfter = 2
        styles["BodyText"].fontSize = 9.8
        styles["BodyText"].leading = 12.2

    metadata = {
        "title": "MoleculeIQ Innovation Product Story",
        "author": "MoleculeIQ",
        "subject": "Drug Repurposing Intelligence Report",
        "creator": "MoleculeIQ Agentic Pipeline",
        "keywords": "drug repurposing, innovation, clinical trials, patents, FTO",
    }

    if report_data:
        molecule = str(report_data.get("molecule", "unknown")).strip().title()
        indication = str(report_data.get("indication", "unknown")).strip().title()
        metadata["title"] = f"Innovation Product Story - {molecule} for {indication}"
        metadata["keywords"] = f"{molecule}, {indication}, drug repurposing, clinical evidence, patents"

    story: list[Any] = []
    if report_data:
        _build_report(story, styles, report_data)
    else:
        story.append(Paragraph("Innovation Product Story", styles["Title"]))
        story.append(Spacer(1, 6))
        for line in markdown_text.splitlines():
            text = line.strip()
            if not text:
                story.append(Spacer(1, 4))
                continue
            if text.startswith("# "):
                story.append(Paragraph(text[2:], styles["Title"]))
            elif text.startswith("## "):
                story.append(Paragraph(text[3:], styles["Heading2"]))
            elif text.startswith("- "):
                story.append(Paragraph(f"&bull; {text[2:]}", styles["BodyText"]))
            else:
                story.append(Paragraph(text, styles["BodyText"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, d: _render_footer(canvas, d, metadata=metadata),
        onLaterPages=lambda canvas, d: _render_footer(canvas, d, metadata=None),
    )
    return str(output_path)
