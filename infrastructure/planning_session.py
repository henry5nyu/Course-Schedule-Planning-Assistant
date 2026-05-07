from __future__ import annotations

from dataclasses import dataclass, field

from models.course import Course
from models.schedule import Schedule
from models.schedule_preference import SchedulePreference


@dataclass
class PlanningSession:
    """Stores temporary course planning state. Matches Sequence Diagram exactly."""

    selectedCourses: list[Course] = field(default_factory=list)
    preferences: list[SchedulePreference] = field(default_factory=list)
    validSchedules: list[Schedule] = field(default_factory=list)
    preferredSchedule: Schedule | None = None

    def saveDesiredCourses(self, courses: list[Course]) -> None:
        """Matches SD: saveDesiredCourses(selectedCodes) logic"""
        self.selectedCourses = list(courses)

    def loadSelectedCourses(self) -> list[Course]:
        """Matches SD: loadSelectedCourses()"""
        return list(self.selectedCourses)

    def savePreference(self, day: str, startTime: str, endTime: str) -> None:
        """Matches SD: savePreference(day, startTime, endTime)"""
        self.preferences.append(SchedulePreference(day, startTime, endTime))

    def getPreference(self) -> list[SchedulePreference]:
        """Matches SD: getPreference()"""
        return list(self.preferences)

    def saveValidSchedules(self, schedules: list[Schedule]) -> None:
        """Saves valid schedules for later selection"""
        self.validSchedules = list(schedules)

    def findSchedule(self, schedule_id: str) -> Schedule | None:
        """Matches SD (ns6): findSchedule(schedule_id)"""
        normalized = schedule_id.strip().upper()
        for schedule in self.validSchedules:
            if schedule.scheduleId.upper() == normalized: # Make sure schedule object has this property
                return schedule
        return None

    def loadSchedule(self, schedule_id: str) -> Schedule | None:
        """Matches SD (ns6): loadSchedule(schedule_id)"""
        return self.findSchedule(schedule_id)

    def SaveSchedule(self, schedule_id: str) -> None:
        """Matches SD (ns6): SaveSchedule(schedule_id) - Note the Capital S"""
        schedule = self.findSchedule(schedule_id)
        if schedule:
            self.preferredSchedule = schedule
