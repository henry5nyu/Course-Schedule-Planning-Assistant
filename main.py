from controllers.course_planning_controller import CoursePlanningController
from infrastructure.planning_session import PlanningSession
from repositories.course_repository import CourseRepository
from services.course_selection_service import CourseSelectionService
from services.interested_course_service import InterestedCourseService
from services.preference_service import PreferenceService
from services.preferred_selection_service import PreferredSelectionService
from services.schedule_generation_service import ScheduleGenerationService
from ui.command_line_interface import CommandLineInterface
from utils.conflict_checker import ConflictChecker
from utils.schedule_strategy import BruteForceScheduleStrategy
from validators.preference_validator import PreferenceValidator


def main() -> None:
    """Wire dependencies and start the command-line interface."""
    repository = CourseRepository()
    session = PlanningSession()
    validator = PreferenceValidator()
    checker = ConflictChecker()
    strategy = BruteForceScheduleStrategy()

    interested_service = InterestedCourseService(repository, session)
    selection_service = CourseSelectionService(repository, session)
    preference_service = PreferenceService(validator, session)
    generation_service = ScheduleGenerationService(repository, session, checker, strategy)
    preferred_service = PreferredSelectionService(session)

    controller = CoursePlanningController(
        interested_service,
        selection_service,
        preference_service,
        generation_service,
        preferred_service,
        session,
    )

    cli = CommandLineInterface(controller)
    cli.run()


if __name__ == "__main__":
    main()
