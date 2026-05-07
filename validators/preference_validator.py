import re


class PreferenceValidator:
    """Validates preferred/available time preference input."""

    VALID_DAYS = {
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "mon", "tue", "wed", "thu", "fri", "sat", "sun",
    }

    def validate(self, day: str, startTime: str, endTime: str) -> bool:
        """Matches SD: validate(day, startTime, endTime)"""
        if day.strip().lower() not in self.VALID_DAYS:
            return False
        if not self._valid_time(startTime) or not self._valid_time(endTime):
            return False
        return self._timeToMinutes(startTime) < self._timeToMinutes(endTime)

    def _valid_time(self, value: str) -> bool:
        if not re.fullmatch(r"\d{2}:\d{2}", value.strip()):
            return False
        hours, minutes = value.split(":")
        return 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59

    def _timeToMinutes(self, value: str) -> int:
        hours, minutes = value.split(":")
        return int(hours) * 60 + int(minutes)
