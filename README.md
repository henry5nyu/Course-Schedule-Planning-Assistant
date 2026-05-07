# Course Schedule Planning Assistant

## Introduction
The Course Schedule Planning Assistant is an API-driven Python tool designed to help NYU students effortlessly generate conflict-free course schedules. By fetching real-time course data directly from the NYU Bulletin API, the assistant allows users to search for courses, manage an interest list, set availability preferences, and automatically generate valid schedules that meet all constraints.

## Features
- **Course Search (API)**: Fetches real-time course and section data dynamically from the NYU API.
- **Interest List Management**: Users can browse, add, and store courses they are interested in taking.
- **Preference Setting**: Allows users to specify days and time ranges when they are available for classes.
- **Automated Schedule Generation**: Utilizes a Brute Force Strategy to build all possible combinations of selected courses.
- **Conflict Checking**: Automatically filters out schedules with overlapping sections or preference violations, returning only strictly valid options.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Course-Schedule-Planning-Assistant
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the program from the root directory via the command line:
```bash
python main.py
```
Follow the interactive prompts in the terminal to browse courses, set preferences, and generate your schedule.

## System Architecture
The application is built using a strict **Layered Architecture** adhering to **SOLID** principles:
- **UI (Command Line Interface)**: Manages user interaction and console output.
- **Controller**: Acts as the bridge between the UI and business logic, delegating tasks.
- **Services**: Encapsulates core business workflows (e.g., `ScheduleGenerationService`, `PreferenceService`).
- **Repository**: Manages data persistence and external API calls (`ICourseRepository`).
- **Infrastructure**: Maintains session state during the planning flow (`PlanningSession`).
- **Models**: Defines domain entities (`Course`, `Section`, `Schedule`, etc.) using pure Python `@dataclass`.
- **Utils & Validators**: Contains standalone logic like `ConflictChecker` and `ScheduleStrategy`.

This separation of concerns ensures that business logic is fully decoupled from the UI and external APIs, making the system highly testable, maintainable, and scalable. The codebase tightly aligns with the provided Sequence and Class Diagrams, utilizing strict `camelCase` naming conventions for class methods and attributes.