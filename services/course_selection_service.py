from repositories.course_repository import ICourseRepository
from infrastructure.planning_session import PlanningSession

class CourseSelectionService:
    """Handles selecting desired courses from the interested list."""

    def __init__(
        self, course_repository: ICourseRepository, planning_session: PlanningSession
    ) -> None:
        self.courseRepository = course_repository
        self.planningSession = planning_session

    def selectCourses(self, selectedCodes: list[str]) -> bool:
        """Matches SD: selectCourses(selectedCodes)"""
        # SD (browseCourse_sqd.pdf) shows fetchInterestedCourses() is called on ICourseRepository
        interested = self.courseRepository.fetchInterestedCourses()
        interested_by_code = {course.courseCode.upper(): course for course in interested}

        selected_courses = []
        for code in selectedCodes:
            normalized = code.strip().upper()
            if normalized not in interested_by_code:
                return False
            selected_courses.append(interested_by_code[normalized])

        # Matches SD: saveDesiredCourses(selectedCodes) -> We pass objects here based on logic
        self.planningSession.saveDesiredCourses(selected_courses)
        return True