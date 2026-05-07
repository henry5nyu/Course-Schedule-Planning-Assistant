from models.course_option import CourseOption
from models.schedule import Schedule
from models.schedule_preference import SchedulePreference
from models.section import Section


class ConflictChecker:
    """Checks schedule section conflicts and preference violations."""

    def removeConflict(
        self, rawCombinations: list[Schedule], preference: list[SchedulePreference]
    ) -> list[Schedule]:
        """Matches SD (ns5): removeConflict(rawCombinations, preference)"""
        return [
            schedule for schedule in rawCombinations
            if not self._has_conflict(schedule, preference)
        ]

    def _has_conflict(self, schedule: Schedule, preferences: list[SchedulePreference]) -> bool:
        options = schedule.getCourseOptions()
        for option in options:
            if self._violates_preferences(option, preferences):
                return True
            if self._internal_sections_conflict(option.getAllSections()):
                return True

        for index, option in enumerate(options):
            for other in options[index + 1 :]:
                if self._course_options_conflict(option, other):
                    return True
        return False

    def _course_options_conflict(
        self, option_a: CourseOption, option_b: CourseOption
    ) -> bool:
        for section_a in option_a.getAllSections():
            for section_b in option_b.getAllSections():
                if self._sections_conflict(section_a, section_b):
                    return True
        return False

    def _sections_conflict(self, section_a: Section, section_b: Section) -> bool:
        for slot_a in section_a.getTimeSlots():
            for slot_b in section_b.getTimeSlots():
                if slot_a.overlapsWith(slot_b):
                    return True
        return False

    def _violates_preferences(
        self, option: CourseOption, preferences: list[SchedulePreference]
    ) -> bool:
        if not preferences:
            return False
            
        preference_slots = [preference.toTimeSlot() for preference in preferences]
        for section in option.getAllSections():
            for section_slot in section.getTimeSlots():
                is_valid = False
                for preference_slot in preference_slots:
                    if section_slot.fallsWithin(preference_slot):
                        is_valid = True
                        break
                
                if not is_valid:
                    return True
        return False

    def _internal_sections_conflict(self, sections: list[Section]) -> bool:
        for index, section in enumerate(sections):
            for other in sections[index + 1 :]:
                if self._sections_conflict(section, other):
                    return True
        return False
