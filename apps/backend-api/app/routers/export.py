"""
Export Router.

Provides endpoints for exporting interpretation results
as deterministic PDF reports.
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from app.services.genai_interpreter import GenAIInterpreterService
from app.services.pdf_exporter import PdfExporterService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/export", tags=["export"])

genai_service = GenAIInterpreterService()
pdf_exporter = PdfExporterService()


# ------------------------------------------------------------
# Request model
# ------------------------------------------------------------

class PdfExportRequest(BaseModel):
    """
    Request payload for PDF export.
    """
    subject_type: str = Field(
        ...,
        description="Type of subject to export: 'vin' or 'cohort'."
    )
    subject_id: str = Field(
        ...,
        description="VIN or cohort identifier."
    )


# ------------------------------------------------------------
# Endpoint
# ------------------------------------------------------------

@router.post("/pdf")
def export_pdf(request: PdfExportRequest) -> Response:
    """
    POST /export/pdf

    Generates a PDF report for a VIN or cohort
    and returns it as a binary response.
    """

    subject_type = request.subject_type.lower()

    try:
        if subject_type == "vin":
            interpretation = genai_service.interpret_vin(
                vin=request.subject_id,
                reference_map={},  # injected later via reference loader
            )
            pdf_bytes = pdf_exporter.export_vin_report(interpretation)

        elif subject_type == "cohort":
            interpretation = genai_service.interpret_cohort(
                cohort_id=request.subject_id
            )
            pdf_bytes = pdf_exporter.export_cohort_report(interpretation)

        else:
            raise HTTPException(
                status_code=400,
                detail="subject_type must be 'vin' or 'cohort'."
            )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{subject_type}-'
                    f'{request.subject_id}.pdf"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("PDF export failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF export.",
        ) from exc
