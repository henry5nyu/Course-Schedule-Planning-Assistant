from __future__ import annotations

from infrastructure.planning_session import PlanningSession
from models.schedule import Schedule

class PreferredSelectionService:
    """Handles choosing one schedule from generated valid schedules."""

    def __init__(self, planning_session: PlanningSession) -> None:
        self.planningSession = planning_session

    def chooseSchedule(self, schedule_id: str) -> Schedule | None:
        """Matches SD: chooseSchedule(schedule_id)"""
        # Matches SD (ns6(1).pdf): findSchedule(schedule_id)
        schedule = self.planningSession.findSchedule(schedule_id)
        if schedule is None:
            return None
        # Matches SD (ns6(1).pdf): SaveSchedule(schedule_id) Note the capital 'S'!
        self.planningSession.SaveSchedule(schedule_id)
        return schedule
