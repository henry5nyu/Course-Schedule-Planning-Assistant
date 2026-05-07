from __future__ import annotations

from dataclasses import dataclass

from models.time_slot import TimeSlot


@dataclass(frozen=True)
class SchedulePreference:
    """Represents an unavailable time block selected by the user."""

    day: str
    startTime: str
    endTime: str

    def toTimeSlot(self) -> TimeSlot:
        """Convert the preference into a TimeSlot for conflict checking."""
        return TimeSlot(self.day, self.startTime, self.endTime)

    def __str__(self) -> str:
        return f"Unavailable: {self.day} {self.startTime}-{self.endTime}"
