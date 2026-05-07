from models.course import Course
from repositories.course_repository import ICourseRepository
from infrastructure.planning_session import PlanningSession

class InterestedCourseService:
    """Handles adding and browsing interested courses."""

    def __init__(
        self, course_repository: ICourseRepository, planning_session: PlanningSession
    ) -> None:
        self.courseRepository = course_repository
        self.planningSession = planning_session

    def addCourse(self, courseCode: str) -> bool:
        """Matches SD: addCourse(courseCode)"""
        # Matches SD (addCourse_sqd.pdf): findCourseByCode(courseCode)
        course = self.courseRepository.findCourseByCode(courseCode)
        if course is None:
            return False
        # Matches SD (addCourse_sqd.pdf): saveToInterestedList(course) is called on ICR
        return self.courseRepository.saveToInterestedList(course)

    def getAllInterestedCourses(self) -> list[Course]:
        """Matches SD: getAllInterestedCourses()"""
        # Matches SD (browseCourse_sqd.pdf): fetchInterestedCourses()
        return self.courseRepository.fetchInterestedCourses()
