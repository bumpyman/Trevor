"""FHIR client for interacting with HAPI FHIR server."""
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.observation import Observation
from fhirclient.models.careplan import CarePlan
from fhirclient.models.communicationrequest import CommunicationRequest
from fhirclient.models.humanname import HumanName
from fhirclient.models.identifier import Identifier
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.fhirdate import FHIRDate
from datetime import datetime
from typing import Optional, Dict, List
from loguru import logger
from src.config import settings


class TrevorFHIRClient:
    """Wrapper for FHIR operations in Trevor Bot."""

    def __init__(self):
        """Initialize FHIR client."""
        self.settings = {
            "app_id": "trevor_bot",
            "api_base": settings.fhir_base_url,
        }
        self.client = client.FHIRClient(settings=self.settings)
        logger.info(f"FHIR client initialized: {settings.fhir_base_url}")

    def create_patient(
        self,
        given_name: str,
        family_name: str,
        email: Optional[str] = None,
        telegram_id: Optional[str] = None,
        birth_date: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a FHIR Patient resource.

        Args:
            given_name: Patient's first name
            family_name: Patient's last name
            email: Patient's email
            telegram_id: Telegram user ID
            birth_date: Birth date in YYYY-MM-DD format

        Returns:
            FHIR Patient resource ID
        """
        try:
            patient = Patient()

            # Name
            name = HumanName()
            name.given = [given_name]
            name.family = family_name
            patient.name = [name]

            # Identifiers
            identifiers = []

            if telegram_id:
                telegram_identifier = Identifier()
                telegram_identifier.system = "https://telegram.org"
                telegram_identifier.value = telegram_id
                identifiers.append(telegram_identifier)

            if email:
                email_identifier = Identifier()
                email_identifier.system = "mailto"
                email_identifier.value = email
                identifiers.append(email_identifier)

            if identifiers:
                patient.identifier = identifiers

            # Birth date
            if birth_date:
                patient.birthDate = FHIRDate(birth_date)

            # Save to server
            patient.create(self.client.server)

            logger.info(f"Created FHIR Patient: {patient.id}")
            return patient.id

        except Exception as e:
            logger.error(f"Error creating FHIR patient: {e}")
            return None

    def create_observation(
        self,
        patient_id: str,
        observation_type: str,
        value: Dict,
        category: Optional[str] = None,
        effective_datetime: Optional[datetime] = None,
    ) -> Optional[str]:
        """
        Create a FHIR Observation resource.

        Args:
            patient_id: FHIR Patient ID
            observation_type: Type of observation (symptom, vital, questionnaire)
            value: Observation value
            category: Observation category
            effective_datetime: When observation was made

        Returns:
            FHIR Observation resource ID
        """
        try:
            observation = Observation()

            # Subject (patient reference)
            observation.subject = {"reference": f"Patient/{patient_id}"}

            # Status
            observation.status = "final"

            # Code (what was observed)
            code = CodeableConcept()
            coding = Coding()
            coding.system = "http://trevorbot.health/observation-types"
            coding.code = observation_type
            coding.display = observation_type
            code.coding = [coding]
            observation.code = code

            # Category
            if category:
                cat_concept = CodeableConcept()
                cat_coding = Coding()
                cat_coding.system = "http://trevorbot.health/observation-categories"
                cat_coding.code = category
                cat_coding.display = category
                cat_concept.coding = [cat_coding]
                observation.category = [cat_concept]

            # Effective date/time
            if effective_datetime:
                observation.effectiveDateTime = FHIRDate(effective_datetime.isoformat())
            else:
                observation.effectiveDateTime = FHIRDate(datetime.utcnow().isoformat())

            # Value (stored as note for flexibility)
            from fhirclient.models.annotation import Annotation

            note = Annotation()
            note.text = str(value)
            observation.note = [note]

            # Save to server
            observation.create(self.client.server)

            logger.info(f"Created FHIR Observation: {observation.id}")
            return observation.id

        except Exception as e:
            logger.error(f"Error creating FHIR observation: {e}")
            return None

    def create_care_plan(
        self,
        patient_id: str,
        title: str,
        description: str,
        goals: List[str],
    ) -> Optional[str]:
        """
        Create a FHIR CarePlan resource.

        Args:
            patient_id: FHIR Patient ID
            title: Care plan title
            description: Care plan description
            goals: List of goal descriptions

        Returns:
            FHIR CarePlan resource ID
        """
        try:
            care_plan = CarePlan()

            # Subject (patient reference)
            care_plan.subject = {"reference": f"Patient/{patient_id}"}

            # Status
            care_plan.status = "active"

            # Intent
            care_plan.intent = "plan"

            # Title
            care_plan.title = title

            # Description
            care_plan.description = description

            # Goals (as notes for simplicity)
            from fhirclient.models.annotation import Annotation

            notes = []
            for goal in goals:
                note = Annotation()
                note.text = f"Goal: {goal}"
                notes.append(note)

            if notes:
                care_plan.note = notes

            # Period
            from fhirclient.models.period import Period

            period = Period()
            period.start = FHIRDate(datetime.utcnow().isoformat())
            care_plan.period = period

            # Save to server
            care_plan.create(self.client.server)

            logger.info(f"Created FHIR CarePlan: {care_plan.id}")
            return care_plan.id

        except Exception as e:
            logger.error(f"Error creating FHIR care plan: {e}")
            return None

    def create_communication_request(
        self,
        patient_id: str,
        reason: str,
        urgency: str,
        preferred_times: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Create a FHIR CommunicationRequest for HUG@Home appointments.

        Args:
            patient_id: FHIR Patient ID
            reason: Reason for appointment
            urgency: Urgency level (routine, urgent, asap)
            preferred_times: List of preferred appointment times

        Returns:
            FHIR CommunicationRequest resource ID
        """
        try:
            comm_request = CommunicationRequest()

            # Subject (patient reference)
            comm_request.subject = {"reference": f"Patient/{patient_id}"}

            # Status
            comm_request.status = "active"

            # Priority
            priority_map = {
                "routine": "routine",
                "urgent": "urgent",
                "very_urgent": "asap",
            }
            comm_request.priority = priority_map.get(urgency, "routine")

            # Payload (reason and preferred times)
            from fhirclient.models.communicationrequest import (
                CommunicationRequestPayload,
            )
            from fhirclient.models.annotation import Annotation

            payload = CommunicationRequestPayload()

            # Add reason as contentString
            content = f"Raison: {reason}\n"
            if preferred_times:
                content += "Disponibilités:\n" + "\n".join(preferred_times)

            payload.contentString = content
            comm_request.payload = [payload]

            # Note
            note = Annotation()
            note.text = f"HUG@Home appointment request - {urgency}"
            comm_request.note = [note]

            # Occurrence (when it was requested)
            from fhirclient.models.fhirdatetime import FHIRDateTime

            comm_request.occurrenceDateTime = FHIRDateTime(datetime.utcnow().isoformat())

            # Save to server
            comm_request.create(self.client.server)

            logger.info(f"Created FHIR CommunicationRequest: {comm_request.id}")
            return comm_request.id

        except Exception as e:
            logger.error(f"Error creating FHIR communication request: {e}")
            return None

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Retrieve a Patient resource by ID.

        Args:
            patient_id: FHIR Patient ID

        Returns:
            Patient resource or None
        """
        try:
            patient = Patient.read(patient_id, self.client.server)
            return patient
        except Exception as e:
            logger.error(f"Error retrieving patient {patient_id}: {e}")
            return None

    def search_observations(
        self,
        patient_id: str,
        observation_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Observation]:
        """
        Search observations for a patient.

        Args:
            patient_id: FHIR Patient ID
            observation_type: Filter by observation type
            limit: Maximum number of results

        Returns:
            List of Observation resources
        """
        try:
            search = Observation.where(struct={"subject": f"Patient/{patient_id}"})

            if observation_type:
                search = search.where(struct={"code": observation_type})

            observations = search.perform_resources(self.client.server)

            return observations[:limit] if observations else []

        except Exception as e:
            logger.error(f"Error searching observations: {e}")
            return []
