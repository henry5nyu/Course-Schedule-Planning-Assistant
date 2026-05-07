from __future__ import annotations

from dataclasses import dataclass

from models.section import LectureSection, RecitationSection, Section


@dataclass(frozen=True)
class CourseOption:
    """Represents one valid enrollment option for one course."""

    courseCode: str
    lectureSection: LectureSection
    recitationSection: RecitationSection | None = None

    def getAllSections(self) -> list[Section]:
        """Return the lecture and optional recitation for this course option."""
        sections: list[Section] = [self.lectureSection]
        if self.recitationSection is not None:
            sections.append(self.recitationSection)
        return sections

    def __str__(self) -> str:
        recitation_text = (
            f"\n    Recitation: {self.recitationSection}"
            if self.recitationSection is not None
            else "\n    Recitation: None"
        )
        return (
            f"{self.courseCode}\n"
            f"    Lecture: {self.lectureSection}"
            f"{recitation_text}"
        )
