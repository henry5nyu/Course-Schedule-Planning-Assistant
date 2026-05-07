from infrastructure.planning_session import PlanningSession
from models.schedule_preference import SchedulePreference
from validators.preference_validator import PreferenceValidator

class PreferenceService:
    """Handles validating and saving schedule preferences."""

    def __init__(
        self, preference_validator: PreferenceValidator, planning_session: PlanningSession
    ) -> None:
        self.preferenceValidator = preference_validator
        self.planningSession = planning_session

    def savePreference(self, day: str, startTime: str, endTime: str) -> bool:
        """Matches SD: savePreference(day, startTime, endTime)"""
        if not self.preferenceValidator.validate(day, startTime, endTime):
            return False
        # Matches SD: savePreference(day, startTime, endTime)
        self.planningSession.savePreference(day, startTime, endTime)
        return True
