"""Email service for sending HUG@Home appointment requests."""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import List, Optional
from datetime import datetime
from loguru import logger
from src.config import settings


class EmailService:
    """Service for sending emails via SendGrid."""

    def __init__(self):
        """Initialize email service."""
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.from_email = Email(settings.from_email)
        logger.info("Email service initialized")

    def send_hug_home_request(
        self,
        patient_name: str,
        patient_email: str,
        patient_phone: Optional[str],
        reason: str,
        urgency: str,
        preferred_times: List[str],
        medical_context: Optional[str] = None,
    ) -> bool:
        """
        Send HUG@Home appointment request email.

        Args:
            patient_name: Patient's full name
            patient_email: Patient's email
            patient_phone: Patient's phone number
            reason: Reason for consultation
            urgency: Urgency level (routine, urgent, very_urgent)
            preferred_times: List of preferred appointment times
            medical_context: Recent medical context (symptoms, observations)

        Returns:
            True if email sent successfully
        """
        try:
            # Map urgency to French
            urgency_map = {
                "routine": "Routine",
                "urgent": "Urgent",
                "very_urgent": "Très urgent",
            }
            urgency_fr = urgency_map.get(urgency, "Routine")

            # Build email subject
            subject = f"Demande HUG@Home - {patient_name} - {urgency_fr}"

            # Build email body
            body = self._build_email_body(
                patient_name=patient_name,
                patient_email=patient_email,
                patient_phone=patient_phone,
                reason=reason,
                urgency=urgency_fr,
                preferred_times=preferred_times,
                medical_context=medical_context,
            )

            # Create email
            message = Mail(
                from_email=self.from_email,
                to_emails=To(settings.hug_hematology_email),
                subject=subject,
                html_content=Content("text/html", body),
            )

            # Send email
            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(
                    f"HUG@Home appointment request sent for {patient_name} (urgency: {urgency})"
                )
                return True
            else:
                logger.error(f"Failed to send email. Status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending HUG@Home email: {e}")
            return False

    def _build_email_body(
        self,
        patient_name: str,
        patient_email: str,
        patient_phone: Optional[str],
        reason: str,
        urgency: str,
        preferred_times: List[str],
        medical_context: Optional[str],
    ) -> str:
        """Build HTML email body."""
        phone_section = (
            f"<p><strong>Téléphone:</strong> {patient_phone}</p>"
            if patient_phone
            else ""
        )

        medical_context_section = ""
        if medical_context:
            medical_context_section = f"""
            <div style="background-color: #f0f8ff; padding: 15px; margin: 20px 0; border-left: 4px solid #0066cc;">
                <h3 style="margin-top: 0; color: #0066cc;">Contexte médical récent:</h3>
                <p>{medical_context}</p>
            </div>
            """

        preferred_times_list = "".join([f"<li>{time}</li>" for time in preferred_times])

        urgency_color = {
            "Routine": "#28a745",
            "Urgent": "#ffc107",
            "Très urgent": "#dc3545",
        }.get(urgency, "#6c757d")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #0066cc;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 30px;
                    border: 1px solid #ddd;
                    border-radius: 0 0 5px 5px;
                }}
                .urgency-badge {{
                    display: inline-block;
                    padding: 5px 15px;
                    background-color: {urgency_color};
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .section h3 {{
                    color: #0066cc;
                    margin-bottom: 10px;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                ul li {{
                    padding: 5px 0;
                    padding-left: 20px;
                    position: relative;
                }}
                ul li:before {{
                    content: "📅";
                    position: absolute;
                    left: 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Demande de rendez-vous HUG@Home</h1>
                    <p>Via TrevorBot - Assistant Drépanocytose</p>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>Une demande de rendez-vous HUG@Home a été soumise via TrevorBot pour le patient suivant:</p>

                    <div class="section">
                        <h3>👤 Informations du patient</h3>
                        <p><strong>Nom:</strong> {patient_name}</p>
                        <p><strong>Email:</strong> {patient_email}</p>
                        {phone_section}
                        <p><strong>Urgence:</strong> <span class="urgency-badge">{urgency}</span></p>
                        <p><strong>Date de la demande:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                    </div>

                    <div class="section">
                        <h3>🩺 Raison de la consultation</h3>
                        <p>{reason}</p>
                    </div>

                    {medical_context_section}

                    <div class="section">
                        <h3>📅 Disponibilités proposées</h3>
                        <ul>
                            {preferred_times_list}
                        </ul>
                    </div>

                    <div class="section" style="background-color: #fff3cd; padding: 15px; border-radius: 5px;">
                        <p style="margin: 0;"><strong>Note:</strong> Cette demande provient du système automatisé TrevorBot.
                        Merci de confirmer le rendez-vous directement avec le patient par email ou téléphone.</p>
                    </div>

                    <div class="footer">
                        <p>Ce message a été généré automatiquement par TrevorBot</p>
                        <p>Service d'hématologie - HUG</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_confirmation_to_patient(
        self,
        patient_email: str,
        patient_name: str,
        appointment_details: str,
    ) -> bool:
        """
        Send appointment confirmation to patient.

        Args:
            patient_email: Patient's email
            patient_name: Patient's name
            appointment_details: Details of the scheduled appointment

        Returns:
            True if email sent successfully
        """
        try:
            subject = "Confirmation de votre demande HUG@Home - TrevorBot"

            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #0066cc;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #ffffff;
                        padding: 30px;
                        border: 1px solid #ddd;
                        border-radius: 0 0 5px 5px;
                    }}
                    .success-box {{
                        background-color: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Demande bien reçue</h1>
                    </div>
                    <div class="content">
                        <p>Bonjour {patient_name},</p>

                        <div class="success-box">
                            <p><strong>✓ Ta demande de rendez-vous HUG@Home a bien été envoyée au service d'hématologie.</strong></p>
                        </div>

                        <p><strong>Détails de ta demande:</strong></p>
                        <p>{appointment_details}</p>

                        <p><strong>Prochaines étapes:</strong></p>
                        <ol>
                            <li>Le service d'hématologie HUG va examiner ta demande</li>
                            <li>Tu seras contacté par email ou téléphone pour confirmer le rendez-vous</li>
                            <li>Délai habituel de réponse: 1-2 jours ouvrables</li>
                        </ol>

                        <p style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px;">
                            <strong>⚠️ Important:</strong> Si ta situation nécessite une attention urgente,
                            n'hésite pas à appeler directement le service d'hématologie HUG ou le 144 en cas d'urgence.
                        </p>

                        <p>Je reste à ta disposition pour toute question!</p>

                        <p>Prends soin de toi,<br>
                        <strong>Trevor 🤖</strong></p>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=self.from_email,
                to_emails=To(patient_email),
                subject=subject,
                html_content=Content("text/html", body),
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Confirmation email sent to {patient_email}")
                return True
            else:
                logger.error(
                    f"Failed to send confirmation email. Status: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return False
