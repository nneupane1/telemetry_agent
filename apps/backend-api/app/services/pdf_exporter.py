"""
PDF Exporter Service.

Generates forensic-grade, immutable PDF documents from Action Packs.
Designed for audit, executive review, and operational delivery.
"""

from __future__ import annotations

from io import BytesIO
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)

from app.models.action_pack import ActionPack
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class PdfExportError(RuntimeError):
    pass


class PdfExporter:
    """
    Service responsible for Action Pack PDF generation.
    """

    def __init__(self) -> None:
        self._styles = getSampleStyleSheet()

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def generate(
        self,
        *,
        action_pack: ActionPack,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate a PDF from an Action Pack.
        Returns PDF bytes and optionally writes to disk.
        """

        log_event(
            logger,
            "Starting PDF generation",
            extra={
                "action_pack_id": action_pack.action_pack_id,
                "subject_id": action_pack.subject_id,
            },
        )

        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                title=action_pack.title,
                author="GenAI Predictive Interpreter Platform",
            )

            story = []
            self._build_header(story, action_pack)
            self._build_summary(story, action_pack)
            self._build_recommendations(story, action_pack)
            self._build_approval(story, action_pack)

            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            if output_path:
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)

            log_event(
                logger,
                "PDF generation completed",
                extra={
                    "action_pack_id": action_pack.action_pack_id,
                    "bytes": len(pdf_bytes),
                },
            )

            return pdf_bytes

        except Exception as exc:
            raise PdfExportError("Failed to generate Action Pack PDF") from exc

    # -----------------------------------------------------------------
    # Internal builders
    # -----------------------------------------------------------------

    def _build_header(self, story, action_pack: ActionPack) -> None:
        story.append(
            Paragraph(
                f"<b>{action_pack.title}</b>",
                self._styles["Title"],
            )
        )
        story.append(
            Paragraph(
                f"Subject: {action_pack.subject_type} — {action_pack.subject_id}",
                self._styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"Generated at: {action_pack.generated_at.isoformat()}",
                self._styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

    def _build_summary(self, story, action_pack: ActionPack) -> None:
        story.append(
            Paragraph("<b>Executive Summary</b>", self._styles["Heading2"])
        )
        story.append(
            Paragraph(
                action_pack.executive_summary,
                self._styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

    def _build_recommendations(self, story, action_pack: ActionPack) -> None:
        story.append(
            Paragraph("<b>Recommendations</b>", self._styles["Heading2"])
        )

        items = []
        for rec in action_pack.recommendations:
            items.append(
                ListItem(
                    Paragraph(
                        f"<b>{rec.title}</b><br/>{rec.rationale}",
                        self._styles["Normal"],
                    )
                )
            )

        story.append(ListFlowable(items, bulletType="bullet"))
        story.append(Spacer(1, 12))

    def _build_approval(self, story, action_pack: ActionPack) -> None:
        if not action_pack.approval:
            return

        story.append(
            Paragraph("<b>Approval</b>", self._styles["Heading2"])
        )
        story.append(
            Paragraph(
                f"Status: {action_pack.approval.status}",
                self._styles["Normal"],
            )
        )
        if action_pack.approval.approved_by:
            story.append(
                Paragraph(
                    f"Approved by: {action_pack.approval.approved_by}",
                    self._styles["Normal"],
                )
            )
