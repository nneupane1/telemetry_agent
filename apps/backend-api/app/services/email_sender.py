"""
Email Sender Service.

Responsible for secure, auditable delivery of Action Packs
via enterprise SMTP, optionally with PDF attachments.
"""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Iterable, Optional

from app.models.action_pack import ActionPack
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


class EmailSender:
    """
    Service responsible for Action Pack email delivery.
    """

    def __init__(self) -> None:
        self._config = load_config().email

        if not self._config.enabled:
            logger.warning("Email delivery is disabled by configuration")

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def send(
        self,
        *,
        action_pack: ActionPack,
        recipients: Iterable[str],
        pdf_bytes: Optional[bytes] = None,
    ) -> None:
        """
        Send an Action Pack email to recipients.
        """

        if not self._config.enabled:
            log_event(
                logger,
                "Email delivery skipped (disabled)",
                extra={"action_pack_id": action_pack.action_pack_id},
            )
            return

        message = self._build_message(
            action_pack=action_pack,
            recipients=list(recipients),
            pdf_bytes=pdf_bytes,
        )

        try:
            with smtplib.SMTP(self._config.smtp_host, self._config.smtp_port) as server:
                server.starttls()
                if self._config.username and self._config.password:
                    server.login(
                        self._config.username,
                        self._config.password.get_secret_value(),
                    )
                server.send_message(message)

            log_event(
                logger,
                "Action Pack email sent",
                extra={
                    "action_pack_id": action_pack.action_pack_id,
                    "recipient_count": len(list(recipients)),
                },
            )

        except Exception as exc:
            raise EmailDeliveryError(
                "Failed to send Action Pack email"
            ) from exc

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _build_message(
        self,
        *,
        action_pack: ActionPack,
        recipients: list[str],
        pdf_bytes: Optional[bytes],
    ) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = action_pack.title
        msg["From"] = self._config.from_address
        msg["To"] = ", ".join(recipients)

        msg.set_content(
            f"""
Action Pack: {action_pack.title}

Subject: {action_pack.subject_type} — {action_pack.subject_id}

{action_pack.executive_summary}

Generated at: {action_pack.generated_at.isoformat()}
"""
        )

        if pdf_bytes:
            msg.add_attachment(
                pdf_bytes,
                maintype="application",
                subtype="pdf",
                filename=f"{action_pack.action_pack_id}.pdf",
            )

        return msg
