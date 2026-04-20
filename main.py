from __future__ import annotations

import csv
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Tuple


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def parse_time_to_minutes(time_str: str) -> int:
    """Convert HH:MM (24h) string to absolute minutes after midnight."""
    raw = time_str.strip()
    parts = raw.split(":")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM.")

    hour, minute = int(parts[0]), int(parts[1])
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError(f"Invalid time: {time_str}.")
    return hour * 60 + minute


def format_minutes(minutes: int) -> str:
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def normalize_days(days_text: str) -> List[str]:
    """Parse 'Mon,Wed,Fri' or 'mon wed fri' into canonical day abbreviations."""
    chunks = (
        days_text.replace("/", " ")
        .replace(",", " ")
        .replace(";", " ")
        .replace("|", " ")
        .split()
    )
    mapping = {
        "monday": "Mon",
        "mon": "Mon",
        "tuesday": "Tue",
        "tue": "Tue",
        "tues": "Tue",
        "wednesday": "Wed",
        "wed": "Wed",
        "thursday": "Thu",
        "thu": "Thu",
        "thur": "Thu",
        "thurs": "Thu",
        "friday": "Fri",
        "fri": "Fri",
        "saturday": "Sat",
        "sat": "Sat",
        "sunday": "Sun",
        "sun": "Sun",
    }

    resolved = []
    for chunk in chunks:
        key = chunk.strip().lower()
        if key not in mapping:
            raise ValueError(f"Unknown day token: {chunk}")
        canonical = mapping[key]
        if canonical not in resolved:
            resolved.append(canonical)
    return resolved


@dataclass(frozen=True)
class TimeSlot:
    day_of_week: str
    start_time: int
    end_time: int

    def overlaps_with(self, other: "TimeSlot") -> bool:
        if self.day_of_week != other.day_of_week:
            return False
        return self.start_time < other.end_time and other.start_time < self.end_time

    def label(self) -> str:
        return (
            f"{self.day_of_week} {format_minutes(self.start_time)}"
            f"-{format_minutes(self.end_time)}"
        )


@dataclass
class Section:
    section_id: str
    section_type: str
    instructor: str = ""
    notes: str = ""
    time_slots: List[TimeSlot] = field(default_factory=list)

    def add_time_slot(self, time_slot: TimeSlot) -> None:
        self.time_slots.append(time_slot)

    def get_section_info(self) -> str:
        time_summary = ", ".join(slot.label() for slot in self.time_slots) or "TBA"
        return (
            f"{self.section_type} {self.section_id} | "
            f"Instructor: {self.instructor or 'N/A'} | "
            f"Times: {time_summary}"
            + (f" | Notes: {self.notes}" if self.notes else "")
        )


@dataclass
class Course:
    course_code: str
    course_name: str
    sections: List[Section] = field(default_factory=list)
    notes: str = ""

    def add_section(self, section: Section) -> None:
        self.sections.append(section)

    def get_sections(self) -> List[Section]:
        return self.sections

    def get_course_info(self) -> str:
        return f"{self.course_code}: {self.course_name}"

    def remove_section(self, section_id: str) -> bool:
        before = len(self.sections)
        self.sections = [s for s in self.sections if s.section_id != section_id]
        return len(self.sections) < before

    def section_groups(self) -> Dict[str, List[Section]]:
        groups: Dict[str, List[Section]] = {}
        for section in self.sections:
            key = section.section_type.strip().lower()
            groups.setdefault(key, []).append(section)
        return groups


@dataclass
class Schedule:
    enrolled_sections: List[Tuple[Course, Section]] = field(default_factory=list)

    def add_section(self, course: Course, section: Section) -> None:
        self.enrolled_sections.append((course, section))

    def remove_section(self, course_code: str, section_id: str) -> None:
        self.enrolled_sections = [
            (c, s)
            for c, s in self.enrolled_sections
            if not (c.course_code == course_code and s.section_id == section_id)
        ]

    def all_time_slots(self) -> List[Tuple[Course, Section, TimeSlot]]:
        output = []
        for course, section in self.enrolled_sections:
            for slot in section.time_slots:
                output.append((course, section, slot))
        return output

    def display_schedule(self) -> str:
        lines = []
        for course, section in sorted(
            self.enrolled_sections,
            key=lambda item: (item[0].course_code, item[1].section_type, item[1].section_id),
        ):
            lines.append(
                f"{course.course_code} {course.course_name} -> {section.get_section_info()}"
            )
        return "\n".join(lines) if lines else "(Empty schedule)"


class ConflictChecker:
    @staticmethod
    def has_time_conflict(section_a: Section, section_b: Section) -> bool:
        for slot_a in section_a.time_slots:
            for slot_b in section_b.time_slots:
                if slot_a.overlaps_with(slot_b):
                    return True
        return False

    @staticmethod
    def schedule_has_conflict(schedule: Schedule) -> bool:
        sections = [section for _, section in schedule.enrolled_sections]
        for i in range(len(sections)):
            for j in range(i + 1, len(sections)):
                if ConflictChecker.has_time_conflict(sections[i], sections[j]):
                    return True
        return False

    @staticmethod
    def conflicts_with_unavailable(schedule: Schedule, unavailable: List[TimeSlot]) -> bool:
        for _, section, slot in schedule.all_time_slots():
            for blocked in unavailable:
                if slot.overlaps_with(blocked):
                    return True
        return False


@dataclass
class Preferences:
    unavailable_times: List[TimeSlot] = field(default_factory=list)
    preferred_instructors: Dict[str, str] = field(default_factory=dict)


class ScheduleGenerator:
    def __init__(self, target_courses: List[Course], preferences: Preferences | None = None):
        self.target_courses = target_courses
        self.preferences = preferences or Preferences()

    def _course_option_bundles(self, course: Course) -> List[List[Section]]:
        if not course.sections:
            return []

        groups = course.section_groups()
        # Each section_type is treated as one required category (e.g., lecture + recitation).
        grouped_lists = [groups[group_key] for group_key in sorted(groups)]
        bundles = [list(combination) for combination in product(*grouped_lists)]
        return bundles

    def _score_schedule(self, schedule: Schedule) -> int:
        score = 0
        for course, section in schedule.enrolled_sections:
            pref = self.preferences.preferred_instructors.get(course.course_code, "").strip()
            if pref and pref.lower() in section.instructor.lower():
                score += 1
        return score

    def generate_combinations(self) -> List[Schedule]:
        per_course_bundles: List[List[List[Section]]] = []
        for course in self.target_courses:
            bundles = self._course_option_bundles(course)
            if not bundles:
                return []
            per_course_bundles.append(bundles)

        all_valid_schedules: List[Schedule] = []
        for course_bundle_combo in product(*per_course_bundles):
            schedule = Schedule()
            for course, bundle in zip(self.target_courses, course_bundle_combo):
                for section in bundle:
                    schedule.add_section(course, section)

            if ConflictChecker.schedule_has_conflict(schedule):
                continue
            if ConflictChecker.conflicts_with_unavailable(
                schedule, self.preferences.unavailable_times
            ):
                continue
            all_valid_schedules.append(schedule)

        all_valid_schedules.sort(key=lambda sch: self._score_schedule(sch), reverse=True)
        return all_valid_schedules


class CoursePlanningCLI:
    def __init__(self) -> None:
        self.courses: List[Course] = []
        self.preferences = Preferences()
        self.generated_schedules: List[Schedule] = []
        self.selected_schedule: Schedule | None = None

    def run(self) -> None:
        while True:
            self._print_menu()
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.load_courses_from_csv()
            elif choice == "2":
                self.add_course_interactive()
            elif choice == "3":
                self.manage_course_interactive()
            elif choice == "4":
                self.list_courses()
            elif choice == "5":
                self.set_preferences()
            elif choice == "6":
                self.generate_schedules()
            elif choice == "7":
                self.view_generated_schedules()
            elif choice == "8":
                self.select_preferred_schedule()
            elif choice == "9":
                self.show_selected_schedule_timetable()
            elif choice == "0":
                print("Goodbye.")
                return
            else:
                print("Invalid choice. Try again.")

    @staticmethod
    def _print_menu() -> None:
        print("\n=== Course Schedule Planning Assistant ===")
        print("1. Load course data from CSV")
        print("2. Add course manually")
        print("3. Edit/delete course and sections")
        print("4. View desired courses")
        print("5. Set preferences (unavailable times/instructor)")
        print("6. Generate valid schedules")
        print("7. View valid schedules")
        print("8. Select preferred schedule")
        print("9. View selected schedule weekly timetable")
        print("0. Exit")

    def load_courses_from_csv(self) -> None:
        path = input(
            "CSV path (columns: course_code,course_name,section_id,section_type,"
            "instructor,days,start_time,end_time,section_notes): "
        ).strip()
        if not path:
            print("No file path entered.")
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                expected = [
                    "course_code",
                    "course_name",
                    "section_id",
                    "section_type",
                    "instructor",
                    "days",
                    "start_time",
                    "end_time",
                    "section_notes",
                ]
                reader = csv.DictReader(file)
                if reader.fieldnames != expected:
                    raise ValueError(
                        f"Invalid header.\nExpected: {expected}\nGot: {reader.fieldnames}"
                    )

                by_code = {course.course_code: course for course in self.courses}
                for row in reader:
                    course_code = (row.get("course_code") or "").strip()
                    course_name = (row.get("course_name") or "").strip()
                    section_id = (row.get("section_id") or "").strip()
                    section_type = (row.get("section_type") or "").strip()
                    instructor = (row.get("instructor") or "").strip()
                    days_text = (row.get("days") or "").strip()
                    start_text = (row.get("start_time") or "").strip()
                    end_text = (row.get("end_time") or "").strip()
                    section_notes = (row.get("section_notes") or "").strip()
                    if not course_code or not course_name or not section_id or not section_type:
                        raise ValueError(f"Missing required fields in CSV row: {row}")

                    course = by_code.get(course_code)
                    if course is None:
                        course = Course(course_code=course_code, course_name=course_name)
                        by_code[course_code] = course
                        self.courses.append(course)

                    section = Section(
                        section_id=section_id,
                        section_type=section_type,
                        instructor=instructor,
                        notes=section_notes,
                    )
                    days = normalize_days(days_text)
                    start = parse_time_to_minutes(start_text)
                    end = parse_time_to_minutes(end_text)
                    for day in days:
                        section.add_time_slot(TimeSlot(day, start, end))
                    course.add_section(section)
        except (OSError, ValueError) as error:
            print(f"Failed to load CSV: {error}")
            return

        print("Course data loaded successfully.")

    def add_course_interactive(self) -> None:
        course_code = input("Course code (e.g., CS101): ").strip()
        course_name = input("Course name: ").strip()
        course_notes = input("Optional course notes: ").strip()
        if not course_code or not course_name:
            print("Course code and name are required.")
            return

        if self._find_course(course_code):
            print(f"Course {course_code} already exists. Use edit menu to update it.")
            return

        course = Course(course_code=course_code, course_name=course_name, notes=course_notes)
        self.courses.append(course)

        while True:
            if input("Add a section now? (y/n): ").strip().lower() != "y":
                break
            section = self._prompt_section()
            if section:
                course.add_section(section)

        print(f"Added {course.get_course_info()} with {len(course.sections)} sections.")

    def manage_course_interactive(self) -> None:
        course_code = input("Enter course code to edit/delete: ").strip()
        course = self._find_course(course_code)
        if course is None:
            print(f"Course {course_code} not found.")
            return

        print(f"\nManaging {course.get_course_info()}")
        print("1. Add section")
        print("2. Delete section")
        print("3. Update course notes")
        print("4. Delete course")
        choice = input("Choose: ").strip()

        if choice == "1":
            section = self._prompt_section()
            if section:
                course.add_section(section)
                print("Section added.")
        elif choice == "2":
            sec_id = input("Section ID to delete: ").strip()
            if course.remove_section(sec_id):
                print("Section removed.")
            else:
                print("Section not found.")
        elif choice == "3":
            course.notes = input("New course notes: ").strip()
            print("Course notes updated.")
        elif choice == "4":
            self.courses = [c for c in self.courses if c.course_code != course.course_code]
            print("Course deleted.")
        else:
            print("Invalid choice.")

    def list_courses(self) -> None:
        if not self.courses:
            print("No courses added yet.")
            return
        print("\nDesired Courses:")
        for course in sorted(self.courses, key=lambda c: c.course_code):
            print(f"- {course.get_course_info()}")
            if course.notes:
                print(f"  Notes: {course.notes}")
            if not course.sections:
                print("  (No sections yet)")
            for section in course.sections:
                print(f"  - {section.get_section_info()}")

    def set_preferences(self) -> None:
        print("\nSet Preferences")
        print("1. Add unavailable time")
        print("2. Clear unavailable times")
        print("3. Set preferred instructor for a course")
        print("4. Clear instructor preferences")
        choice = input("Choose: ").strip()

        if choice == "1":
            slots = self._prompt_timeslots("unavailable")
            if slots:
                self.preferences.unavailable_times.extend(slots)
                print(f"{len(slots)} unavailable time slot(s) added.")
        elif choice == "2":
            self.preferences.unavailable_times.clear()
            print("Unavailable times cleared.")
        elif choice == "3":
            code = input("Course code: ").strip()
            name = input("Preferred instructor name/keyword: ").strip()
            if code and name:
                self.preferences.preferred_instructors[code] = name
                print("Preference saved.")
            else:
                print("Both fields are required.")
        elif choice == "4":
            self.preferences.preferred_instructors.clear()
            print("Instructor preferences cleared.")
        else:
            print("Invalid choice.")

    def generate_schedules(self) -> None:
        if not self.courses:
            print("Add courses first.")
            return
        generator = ScheduleGenerator(self.courses, self.preferences)
        self.generated_schedules = generator.generate_combinations()
        print(f"Generated {len(self.generated_schedules)} valid schedule(s).")

    def view_generated_schedules(self) -> None:
        if not self.generated_schedules:
            print("No generated schedules. Run option 6 first.")
            return
        for idx, schedule in enumerate(self.generated_schedules, start=1):
            print(f"\nSchedule #{idx}")
            print(schedule.display_schedule())

    def select_preferred_schedule(self) -> None:
        if not self.generated_schedules:
            print("No generated schedules to select from.")
            return
        try:
            idx = int(input(f"Pick schedule number (1-{len(self.generated_schedules)}): ").strip())
        except ValueError:
            print("Invalid number.")
            return
        if idx < 1 or idx > len(self.generated_schedules):
            print("Out of range.")
            return
        self.selected_schedule = self.generated_schedules[idx - 1]
        print(f"Selected schedule #{idx}.")

    def show_selected_schedule_timetable(self) -> None:
        if self.selected_schedule is None:
            print("No preferred schedule selected.")
            return
        print("\nSelected Schedule (List View)")
        print(self.selected_schedule.display_schedule())
        print("\nWeekly Timetable")
        print(render_weekly_timetable(self.selected_schedule))

    def _find_course(self, course_code: str) -> Course | None:
        for course in self.courses:
            if course.course_code == course_code:
                return course
        return None

    def _prompt_section(self) -> Section | None:
        section_id = input("Section ID: ").strip()
        section_type = input("Section type (Lecture/Recitation/Lab): ").strip()
        instructor = input("Instructor (optional): ").strip()
        notes = input("Section notes (optional): ").strip()
        if not section_id or not section_type:
            print("Section ID and type are required.")
            return None

        slots = self._prompt_timeslots("section")
        if slots is None:
            return None
        section = Section(
            section_id=section_id,
            section_type=section_type,
            instructor=instructor,
            notes=notes,
        )
        for slot in slots:
            section.add_time_slot(slot)

        while input("Add another timeslot for this section? (y/n): ").strip().lower() == "y":
            extra_slots = self._prompt_timeslots("section")
            if extra_slots:
                for slot in extra_slots:
                    section.add_time_slot(slot)
        return section

    @staticmethod
    def _prompt_timeslots(label: str) -> List[TimeSlot] | None:
        days_text = input(f"{label.capitalize()} days (e.g., Mon,Wed,Fri): ").strip()
        start = input("Start time (HH:MM 24h): ").strip()
        end = input("End time (HH:MM 24h): ").strip()
        try:
            days = normalize_days(days_text)
            start_m = parse_time_to_minutes(start)
            end_m = parse_time_to_minutes(end)
            if end_m <= start_m:
                raise ValueError("End time must be after start time.")
        except ValueError as error:
            print(f"Invalid timeslot input: {error}")
            return None

        return [TimeSlot(day_of_week=day, start_time=start_m, end_time=end_m) for day in days]


def render_weekly_timetable(schedule: Schedule, start_hour: int = 8, end_hour: int = 20) -> str:
    """Render an ASCII timetable by hour, Monday-Sunday."""
    day_to_slots: Dict[str, List[Tuple[int, int, str]]] = {day: [] for day in DAYS}
    for course, section, slot in schedule.all_time_slots():
        tag = f"{course.course_code}-{section.section_id}"
        day_to_slots[slot.day_of_week].append((slot.start_time, slot.end_time, tag))

    for day in DAYS:
        day_to_slots[day].sort(key=lambda x: (x[0], x[1], x[2]))

    col_width = 12
    header = "Time  | " + " | ".join(day.ljust(col_width) for day in DAYS)
    sep = "-" * len(header)
    lines = [header, sep]

    for hour in range(start_hour, end_hour):
        row_time = f"{hour:02d}:00"
        cells = []
        row_start = hour * 60
        row_end = (hour + 1) * 60
        for day in DAYS:
            block = ""
            for start, end, tag in day_to_slots[day]:
                # Slot touches this hourly row.
                if start < row_end and row_start < end:
                    block = tag
                    break
            cells.append(block[:col_width].ljust(col_width))
        lines.append(f"{row_time} | " + " | ".join(cells))
    return "\n".join(lines)


if __name__ == "__main__":
    CoursePlanningCLI().run()
