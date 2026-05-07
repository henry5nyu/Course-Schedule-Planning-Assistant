from __future__ import annotations

from infrastructure.planning_session import PlanningSession
from models.course import Course
from models.schedule import Schedule
from services.course_selection_service import CourseSelectionService
from services.interested_course_service import InterestedCourseService
from services.preference_service import PreferenceService
from services.preferred_selection_service import PreferredSelectionService
from services.schedule_generation_service import ScheduleGenerationService


class CoursePlanningController:
    """Coordinates CLI actions with application services. Methods strictly follow UML."""

    def __init__(
        self,
        interestedCourseService: InterestedCourseService,
        courseSelectionService: CourseSelectionService,
        preferenceService: PreferenceService,
        scheduleGenerationService: ScheduleGenerationService,
        preferredSelectionService: PreferredSelectionService,
        planningSession: PlanningSession,
    ) -> None:
        self.interestedCourseService = interestedCourseService
        self.courseSelectionService = courseSelectionService
        self.preferenceService = preferenceService
        self.scheduleGenerationService = scheduleGenerationService
        self.preferredSelectionService = preferredSelectionService
        self.planningSession = planningSession

    def addCourseToInterest(self, courseCode: str) -> bool:
        """Matches SD: addCourseToInterest(courseCode)"""
        # Note: We will align the service methods in the next step
        return self.interestedCourseService.addCourse(courseCode)

    def browseInterestedCourses(self) -> list[Course]:
        """Matches SD: browseInterestedCourses()"""
        return self.interestedCourseService.getAllInterestedCourses()

    def chooseCourses(self, selectedCodes: list[str]) -> bool:
        """Matches SD: chooseCourses(selectedCodes)"""
        return self.courseSelectionService.selectCourses(selectedCodes)

    def setPreference(self, day: str, startTime: str, endTime: str) -> bool:
        """Matches SD: setPreference(day, startTime, endTime)"""
        return self.preferenceService.savePreference(day, startTime, endTime)

    def ScheduleGeneration(self) -> list[Schedule]:
        """Matches SD: ScheduleGeneration()"""
        return self.scheduleGenerationService.generateSchedules(
            self.planningSession.loadSelectedCourses(),
            self.planningSession.getPreference(),
        )

    def getPreferredSchedule(self, schedule_id: str) -> Schedule | None:
        """Matches SD: getPreferredSchedule(schedule_id)"""
        return self.preferredSelectionService.chooseSchedule(schedule_id)
