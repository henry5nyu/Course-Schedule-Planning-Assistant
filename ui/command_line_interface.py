from controllers.course_planning_controller import CoursePlanningController
from models.course import Course
from models.schedule import Schedule

class CommandLineInterface:
    """Command-line interface strictly matching UML and Sequence Diagrams."""

    def __init__(self, controller: CoursePlanningController) -> None:
        self.controller = controller

    def run(self) -> None:
        while True:
            self.display_main_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.browseInterestedCourseList()
            elif choice == "2":
                print("Goodbye.")
                break
            else:
                self.displayErrorMessage("Please choose a valid menu option.")

    def display_main_menu(self) -> None:
        print("\nCourse Schedule Planning Assistant")
        print("1. Browse Interested Course List")
        print("2. Exit")

    def browseInterestedCourseList(self) -> None:
        """Matches SD: browseInterestedCourseList()"""
        interested_courses = self.controller.browseInterestedCourses()
        self.displayInterestedCourses(interested_courses)

        while True:
            self.display_browse_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.addCourseToInterestedCourseList()
            elif choice == "2":
                self.chooseDesiredCourses()
            elif choice == "3":
                self.displayInterestedCourses(self.controller.browseInterestedCourses())
            elif choice == "4":
                return
            else:
                self.displayErrorMessage("Please choose a valid menu option.")

    def addCourseToInterestedCourseList(self) -> None:
        """Matches SD: addCourseToInterestedCourseList()"""
        course_code = self.enterCourseCode()
        if self.controller.addCourseToInterest(course_code):
            self.displayConfirmation()
        else:
            self.displayErrorMessage("Course not found or already added.")

    def chooseDesiredCourses(self) -> None:
        """Matches SD: chooseDesiredCourses()"""
        interested_courses = self.controller.browseInterestedCourses()
        selected_codes = self.chooseSelectedCodes(interested_courses)
        
        if not selected_codes:
            self.displayInvalidSelectionMessage()
            return
            
        if self.controller.chooseCourses(selected_codes):
            self.displaySelectedOptions(str(selected_codes))
            self.selected_courses_flow()
        else:
            self.displayInvalidSelectionMessage()

    def selected_courses_flow(self) -> None:
        while True:
            self.display_selected_courses_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                days_str, start_time, end_time = self.enterPrefData()
                import re
                days = [d.strip() for d in re.split(r'[,\s]+', days_str) if d.strip()]
                
                success_count = 0
                for day in days:
                    if self.controller.setPreference(day, start_time, end_time):
                        success_count += 1
                
                if success_count > 0:
                    self.displaySavedPreferences()
                else:
                    self.displayErrorMessage("Invalid day(s) or time range.")
            elif choice == "2":
                self.requestScheduleGeneration()
            elif choice == "3":
                return
            else:
                self.displayErrorMessage("Please choose a valid menu option.")

    def requestScheduleGeneration(self) -> None:
        """Matches SD: requestScheduleGeneration()"""
        schedules = self.controller.ScheduleGeneration()
        if schedules:
            self.displayListOfValidCombinations(schedules)
            self.SelectPreferredSchedule()
        else:
            self.displayNoValidScheduleMessage()

    def SelectPreferredSchedule(self) -> None:
        """Matches SD: SelectPreferredSchedule()"""
        while True:
            self.display_generated_schedules_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                schedule_id = self.enterPreferredSchedule()
                schedule = self.controller.getPreferredSchedule(schedule_id)
                if schedule is None:
                    self.displayErrorMessage("Schedule id not found.")
                else:
                    self.displaySelectedSchedule(schedule)
            elif choice == "2":
                return
            else:
                self.displayErrorMessage("Please choose a valid menu option.")

    # --- CLI Input Prompts (Matching UML) ---
    def enterCourseCode(self) -> str:
        return input("Enter course code: ").strip()

    def chooseSelectedCodes(self, interested_courses: list[Course]) -> list[str]:
        if not interested_courses:
            return []
        self.displayInterestedCourses(interested_courses)
        raw_numbers = input("Enter desired course numbers separated by commas: ")
        selected_codes: list[str] = []
        for raw_number in raw_numbers.split(","):
            number_text = raw_number.strip()
            if not number_text.isdigit():
                return []
            index = int(number_text) - 1
            if 0 <= index < len(interested_courses):
                course_code = interested_courses[index].courseCode
                if course_code not in selected_codes:
                    selected_codes.append(course_code)
        return selected_codes

    def enterPrefData(self) -> tuple[str, str, str]:
        print("\nPlease specify a time period when you are AVAILABLE for classes.")
        days_str = input("Enter day(s) separated by spaces or commas: ").strip()
        start_time = input("Enter start time (HH:MM): ").strip()
        end_time = input("Enter end time (HH:MM): ").strip()
        return days_str, start_time, end_time

    def enterPreferredSchedule(self) -> str:
        return input("Enter preferred schedule id: ").strip()

    # --- Output Display Methods (Matching Sequence Diagram 'Returns') ---
    def displayInterestedCourses(self, courses: list[Course]) -> None:
        if not courses:
            self.displayNoInterestedCourses()
            return
        print("\nInterested Courses:")
        for index, course in enumerate(courses, start=1):
            print(f"{index}. {course.courseCode} - {course.courseName}")

    def displayNoInterestedCourses(self) -> None:
        print("Interested course list is empty.")

    def displaySelectedOptions(self, summary: str) -> None:
        print(f"Selected desired courses: {summary}")

    def displayInvalidSelectionMessage(self) -> None:
        print("Error: Invalid selection. Selected course numbers must be from the interested list.")

    def displayConfirmation(self) -> None:
        print("Success: Action completed.")

    def displayErrorMessage(self, message: str) -> None:
        print(f"Error: {message}")

    def displaySavedPreferences(self) -> None:
        print("Preferences successfully saved.")

    def displayListOfValidCombinations(self, schedules: list[Schedule]) -> None:
        print("\nValid Schedules:")
        for schedule in schedules:
            print(schedule.display())

    def displayNoValidScheduleMessage(self) -> None:
        print("No valid schedule combinations could be generated with the current preferences.")

    def displaySelectedSchedule(self, schedule: Schedule) -> None:
        print("\nPreferred Schedule Saved:")
        print(schedule.display())

    def display_browse_menu(self) -> None:
        print("\nBrowse Interested Course List")
        print("1. Add Course to Interested Course List")
        print("2. Select Desired Courses")
        print("3. Refresh Interested Course List")
        print("4. Back to Main Menu")

    def display_selected_courses_menu(self) -> None:
        print("\nSelected Courses")
        print("1. Set Schedule Preferences")
        print("2. Generate Possible Schedule Combinations")
        print("3. Back to Browse")

    def display_generated_schedules_menu(self) -> None:
        print("\nGenerated Schedules")
        print("1. Select Preferred Schedule")
        print("2. Back")
