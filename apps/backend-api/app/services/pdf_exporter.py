"""
PDF Exporter Service.

Generates high-fidelity, deterministic PDF reports
for VIN and cohort interpretations.

Uses ReportLab (Platypus) for enterprise-safe rendering.
"""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

from app.models.vin import VinInterpretation
from app.models.cohort import CohortInterpretation


class PdfExporterService:
    """
    Responsible for rendering PDF reports from
    interpretation models.
    """

    def __init__(self) -> None:
        self._styles = getSampleStyleSheet()
        self._styles.add(
            ParagraphStyle(
                name="Header",
                fontSize=16,
                spaceAfter=14,
                alignment=TA_LEFT,
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="Body",
                fontSize=10,
                spaceAfter=8,
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="Small",
                fontSize=8,
                textColor=colors.grey,
            )
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def export_vin_report(
        self,
        interpretation: VinInterpretation,
    ) -> bytes:
        """
        Generate a VIN-level PDF report.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        story.extend(self._render_header(
            title="VIN Predictive Maintenance Report",
            subtitle=f"VIN: {interpretation.vin}",
            model_version=interpretation.model_version,
        ))

        story.append(Paragraph(
            f"<b>Summary</b><br/>{interpretation.summary}",
            self._styles["Body"],
        ))

        story.append(Spacer(1, 12))

        story.extend(self._render_recommendations(
            interpretation.recommendations
        ))

        doc.build(story)
        return buffer.getvalue()

    def export_cohort_report(
        self,
        interpretation: CohortInterpretation,
    ) -> bytes:
        """
        Generate a cohort-level PDF report.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        story.extend(self._render_header(
            title="Cohort Predictive Maintenance Report",
            subtitle=f"Cohort: {interpretation.cohort_id}",
            model_version=interpretation.model_version,
        ))

        story.append(Paragraph(
            f"<b>Summary</b><br/>{interpretation.summary}",
            self._styles["Body"],
        ))

        story.append(Spacer(1, 12))

        story.extend(self._render_metrics(
            interpretation.metrics
        ))

        doc.build(story)
        return buffer.getvalue()

    # ---------------------------------------------------------
    # Internal render helpers
    # ---------------------------------------------------------

    def _render_header(
        self,
        *,
        title: str,
        subtitle: str,
        model_version: str,
    ) -> Iterable:
        return [
            Paragraph(title, self._styles["Header"]),
            Paragraph(subtitle, self._styles["Small"]),
            Paragraph(f"Model version: {model_version}", self._styles["Small"]),
            Spacer(1, 16),
        ]

    def _render_recommendations(self, recommendations) -> Iterable:
        story = [
            Paragraph("<b>Recommended Actions</b>", self._styles["Body"]),
            Spacer(1, 6),
        ]

        for rec in recommendations:
            story.append(Paragraph(
                f"<b>{rec.title}</b> ({rec.urgency})",
                self._styles["Body"],
            ))
            story.append(Paragraph(
                rec.rationale,
                self._styles["Body"],
            ))

            if rec.evidence:
                table_data = [["Signal", "Confidence"]]
                for ev in rec.evidence:
                    table_data.append([
                        ev.signal_code,
                        f"{int(ev.confidence * 100)}%",
                    ])

                table = Table(table_data, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]))
                story.append(table)

            story.append(Spacer(1, 10))

        return story

    def _render_metrics(self, metrics) -> Iterable:
        story = [
            Paragraph("<b>Cohort Metrics</b>", self._styles["Body"]),
            Spacer(1, 6),
        ]

        table_data = [["Metric", "Value"]]
        for m in metrics:
            table_data.append([m.name, str(m.value)])

        table = Table(table_data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))

        story.append(table)
        return story
