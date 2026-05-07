from __future__ import annotations

import json
import requests
from abc import ABC, abstractmethod

from models.course import Course
from models.section import LectureSection, RecitationSection
from models.time_slot import TimeSlot


class ICourseRepository(ABC):
    """Interface strictly matching the UML Class Diagram."""

    @abstractmethod
    def fetchCourse(self, selectedCourses: list[str]) -> list[Course]:
        pass

    @abstractmethod
    def fetchInterestedCourses(self) -> list[Course]:
        pass

    @abstractmethod
    def fetchCourseSections(self, selectedCodes: list[str]) -> dict:
        pass

    @abstractmethod
    def findCourseByCode(self, courseCode: str) -> Course | None:
        pass

    @abstractmethod
    def saveToInterestedList(self, course: Course) -> bool:
        pass


class CourseRepository(ICourseRepository):
    """Repository that fetches course data from the NYU API and stores interested list."""

    DAY_MAP = {
        "0": "Monday", "1": "Tuesday", "2": "Wednesday", "3": "Thursday",
        "4": "Friday", "5": "Saturday", "6": "Sunday",
    }

    def __init__(self) -> None:
        self.interestedCourses: list[Course] = []

    def saveToInterestedList(self, course: Course) -> bool:
        """Matches SD (addCourse_sqd): saveToInterestedList(course)"""
        if any(existing.courseCode == course.courseCode for existing in self.interestedCourses):
            return False
        self.interestedCourses.append(course)
        return True

    def fetchInterestedCourses(self) -> list[Course]:
        """Matches SD (browseCourse_sqd): fetchInterestedCourses()"""
        return list(self.interestedCourses)

    def findCourseByCode(self, courseCode: str) -> Course | None:
        """Matches SD (addCourse_sqd): findCourseByCode(courseCode)"""
        url = "https://bulletins.nyu.edu/class-search/api/?page=fose&route=search"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        }
        payload = {
            "other": {"srcdb": "9999"},
            "criteria": [{"field": "alias", "value": courseCode.strip()}]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code != 200:
                return None
            data = response.json()
        except requests.RequestException:
            return None

        results = data.get("results", [])
        if not results:
            return None

        # Existing parsing logic from your old file retained perfectly here
        first_result = results[0]
        actual_code = first_result.get("code", courseCode)
        course_name = first_result.get("title", "Unknown Title")
        target_srcdb = first_result.get("srcdb")

        course = Course(actual_code, course_name)
        current_lecture: LectureSection | None = None

        for result in results:
            if target_srcdb and result.get("srcdb") != target_srcdb:
                continue
            schd = result.get("schd", "").upper()
            section_id = f"{actual_code}-{result.get('no', '')}"
            instructor = result.get("instr", "") or "TBD"
            location = "TBD" 
            
            meeting_times_raw = result.get("meetingTimes", "[]")
            try:
                meeting_times = json.loads(meeting_times_raw)
            except json.JSONDecodeError:
                meeting_times = []

            time_slots: list[TimeSlot] = []
            for mt in meeting_times:
                day = self.DAY_MAP.get(str(mt.get("meet_day", "")), "Unknown")
                start_raw = str(mt.get("start_time", ""))
                end_raw = str(mt.get("end_time", ""))
                
                start_time = f"{start_raw.zfill(4)[:2]}:{start_raw.zfill(4)[2:]}" if start_raw else "00:00"
                end_time = f"{end_raw.zfill(4)[:2]}:{end_raw.zfill(4)[2:]}" if end_raw else "00:00"

                if day != "Unknown":
                    time_slots.append(TimeSlot(day, start_time, end_time))

            if schd in ["LEC", "SEM", "CL", "STU", "FLD", "IND"]:
                current_lecture = LectureSection(section_id, schd, instructor, location)
                for slot in time_slots:
                    current_lecture.addTimeSlot(slot)
                course.addLectureSection(current_lecture)
            elif schd in ["RCT", "LAB"]:
                recitation = RecitationSection(section_id, schd, instructor, location)
                for slot in time_slots:
                    recitation.addTimeSlot(slot)
                if current_lecture is not None:
                    current_lecture.addRecitationSection(recitation)
                else:
                    dummy_lecture = LectureSection(f"{actual_code}-Generic", "LEC", "Unknown", "Unknown")
                    dummy_lecture.addRecitationSection(recitation)
                    course.addLectureSection(dummy_lecture)
                    current_lecture = dummy_lecture
            else:
                current_lecture = LectureSection(section_id, schd, instructor, location)
                for slot in time_slots:
                    current_lecture.addTimeSlot(slot)
                course.addLectureSection(current_lecture)

        return course

    def fetchCourse(self, selectedCourses: list[str]) -> list[Course]:
        """Matches UML: fetchCourse(selectedCourses)"""
        courses = []
        for code in selectedCourses:
            course = self.findCourseByCode(code)
            if course is not None:
                courses.append(course)
        return courses

    def fetchCourseSections(self, selectedCodes: list[str]) -> dict:
        """Matches SD: fetchCourseSections(selectedCodes)"""
        courses = self.fetchCourse(selectedCodes)
        return {course.courseCode: course.getLectureSections() for course in courses}
