from infrastructure.planning_session import PlanningSession
from models.course import Course
from models.schedule import Schedule
from models.schedule_preference import SchedulePreference
from repositories.course_repository import ICourseRepository
from utils.conflict_checker import ConflictChecker
from utils.schedule_strategy import ScheduleStrategy

class ScheduleGenerationService:
    """Builds and filters possible course schedules."""

    def __init__(
        self,
        courseRepository: ICourseRepository,
        planningSession: PlanningSession,
        conflictChecker: ConflictChecker,
        scheduleStrategy: ScheduleStrategy,
    ) -> None:
        self.courseRepository = courseRepository
        self.planningSession = planningSession
        self.conflictChecker = conflictChecker
        self.scheduleStrategy = scheduleStrategy

    def generateSchedules(
        self, selectedCourses: list[Course], preferences: list[SchedulePreference]
    ) -> list[Schedule]:
        """Matches SD: generateSchedules(selectedCourses, preferences)"""
        if not selectedCourses:
            self.planningSession.saveValidSchedules([])
            return []

        # Matches SD (ns5(2).pdf): buildRawCombinations(selectedCourses)
        rawCombinations = self.scheduleStrategy.buildRawCombinations(selectedCourses)
        
        # Matches SD (ns5(2).pdf): removeConflict(rawCombinations, preference)
        valid_schedules = self.conflictChecker.removeConflict(rawCombinations, preferences)
        
        self.planningSession.saveValidSchedules(valid_schedules)
        return valid_schedules
