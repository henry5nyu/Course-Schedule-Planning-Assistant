from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSlot:
    """Represents one day/time interval for a course section."""

    day: str
    startTime: str
    endTime: str

    def overlapsWith(self, other: "TimeSlot") -> bool:
        """Return True when two slots are on the same day and overlap."""
        if self.day.strip().lower() != other.day.strip().lower():
            return False

        return (
            self._timeToMinutes(self.startTime) < self._timeToMinutes(other.endTime)
            and other._timeToMinutes(other.startTime) < self._timeToMinutes(self.endTime)
        )

    def fallsWithin(self, other: "TimeSlot") -> bool:
        """Return True if this time slot is completely contained within the other time slot."""
        if self.day.strip().lower() != other.day.strip().lower():
            return False

        return (
            self._timeToMinutes(self.startTime) >= self._timeToMinutes(other.startTime)
            and self._timeToMinutes(self.endTime) <= self._timeToMinutes(other.endTime)
        )

    @staticmethod
    def _timeToMinutes(time_text: str) -> int:
        """Convert HH:MM text into minutes after midnight."""
        hours, minutes = time_text.split(":")
        return int(hours) * 60 + int(minutes)

    def __str__(self) -> str:
        return f"{self.day} {self.startTime}-{self.endTime}"
