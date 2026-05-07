from __future__ import annotations

from dataclasses import dataclass, field

from models.course_option import CourseOption


@dataclass
class Schedule:
    """Represents one complete possible schedule."""

    scheduleId: str
    courseOptions: list[CourseOption] = field(default_factory=list)

    def addCourseOption(self, option: CourseOption) -> None:
        """Add one selected course option to the schedule."""
        self.courseOptions.append(option)

    def getCourseOptions(self) -> list[CourseOption]:
        """Return course options in this schedule."""
        return list(self.courseOptions)

    def display(self) -> str:
        """Return a readable multi-line schedule summary."""
        lines = [f"Schedule {self.scheduleId}"]
        for option in self.courseOptions:
            lines.append(f"  - {option}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.display()
