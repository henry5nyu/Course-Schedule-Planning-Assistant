from __future__ import annotations

from dataclasses import dataclass, field

from models.time_slot import TimeSlot


@dataclass
class Section:
    """Base class for lecture and recitation sections."""

    sectionId: str
    type: str
    instructor: str
    location: str
    timeSlots: list[TimeSlot] = field(default_factory=list)

    def addTimeSlot(self, time_slot: TimeSlot) -> None:
        """Add a meeting time to this section."""
        self.timeSlots.append(time_slot)

    def getTimeSlots(self) -> list[TimeSlot]:
        """Return this section's meeting times."""
        return list(self.timeSlots)

    def __str__(self) -> str:
        slots = ", ".join(str(slot) for slot in self.timeSlots)
        return (
            f"{self.sectionId} ({self.type}) with {self.instructor} "
            f"at {self.location}: {slots}"
        )


@dataclass
class RecitationSection(Section):
    """Represents a recitation section belonging to one lecture section."""


@dataclass
class LectureSection(Section):
    """Represents a lecture section and its corresponding recitations."""

    recitationSections: list[RecitationSection] = field(default_factory=list)

    def addRecitationSection(self, recitation: RecitationSection) -> None:
        """Add a recitation that belongs to this lecture."""
        self.recitationSections.append(recitation)

    def getRecitationSections(self) -> list[RecitationSection]:
        """Return recitations belonging to this lecture."""
        return list(self.recitationSections)
