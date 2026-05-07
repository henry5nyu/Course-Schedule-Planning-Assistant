from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import product

from models.course import Course
from models.course_option import CourseOption
from models.schedule import Schedule


class ScheduleStrategy(ABC):
    """Interface for schedule generation algorithms."""

    @abstractmethod
    def buildRawCombinations(self, selectedCourses: list[Course]) -> list[Schedule]:
        """Matches SD: buildRawCombinations(selectedCourses)"""
        pass


class BruteForceScheduleStrategy(ScheduleStrategy):
    """Generates every possible one-section-per-course combination."""

    def buildRawCombinations(self, selectedCourses: list[Course]) -> list[Schedule]:
        """Matches SD (ns5): buildRawCombinations(selectedCourses)"""
        if not selectedCourses:
            return []

        course_option_groups = [
            self._build_course_options(course) for course in selectedCourses
        ]
        if any(not options for options in course_option_groups):
            return []

        schedules: list[Schedule] = []
        for index, combination in enumerate(product(*course_option_groups), start=1):
            schedules.append(Schedule(f"S{index}", list(combination)))
        return schedules

    def _build_course_options(self, course: Course) -> list[CourseOption]:
        options: list[CourseOption] = []
        for lecture in course.getLectureSections():
            recitations = lecture.getRecitationSections()
            if recitations:
                for recitation in recitations:
                    options.append(CourseOption(course.courseCode, lecture, recitation))
            else:
                options.append(CourseOption(course.courseCode, lecture, None))
        return options
