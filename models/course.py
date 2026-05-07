from __future__ import annotations

from dataclasses import dataclass, field

from models.section import LectureSection


@dataclass
class Course:
    """Represents a course and its possible lecture sections."""

    courseCode: str
    courseName: str
    lectureSections: list[LectureSection] = field(default_factory=list)

    def addLectureSection(self, section: LectureSection) -> None:
        """Add a lecture section option to the course."""
        self.lectureSections.append(section)

    def getLectureSections(self) -> list[LectureSection]:
        """Return available lecture section options."""
        return list(self.lectureSections)

    def __str__(self) -> str:
        return (
            f"{self.courseCode} - {self.courseName} "
            f"({len(self.lectureSections)} lecture sections)"
        )
