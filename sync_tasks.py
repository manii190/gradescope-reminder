import asyncio
import json
import os
import hashlib
from google_tasks import get_tasks_service
from google_calendar import get_calendar_service
from assignments import get_all_assignments

SYNC_FILE = "synced_assignments.json"


def load_synced():
    if not os.path.exists(SYNC_FILE):
        return []

    with open(SYNC_FILE, "r") as file:
        return json.load(file)


def save_synced(synced):
    with open(SYNC_FILE, "w") as file:
        json.dump(synced, file, indent=4)


def clean_course_name(course):
    return course.split("\n")[0].strip()


def make_assignment_id(a):
    course = clean_course_name(a["course_short"])
    return course + "|" + a["name"] + "|" + a["due_date_raw"]


def make_google_event_id(assignment_id):
    return "gs" + hashlib.md5(assignment_id.encode()).hexdigest()


async def main():
    synced = load_synced()

    tasks_service = get_tasks_service()
    calendar_service = get_calendar_service()

    assignments = await get_all_assignments()

    for a in assignments:
        course = clean_course_name(a["course_short"])
        assignment_id = make_assignment_id(a)
        event_id = make_google_event_id(assignment_id)

        title = course + " — " + a["name"]

        event = {
            "id": event_id,
            "summary": title,
            "description": "Gradescope link: " + a.get("link", ""),
            "start": {
                "dateTime": a["due_date_iso"],
                "timeZone": "America/Phoenix"
            },
            "end": {
                "dateTime": a["due_date_iso"],
                "timeZone": "America/Phoenix"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 2880},
                    {"method": "popup", "minutes": 1440},
                    {"method": "popup", "minutes": 360}
                ]
            }
        }

        try:
            calendar_service.events().update(
                calendarId="primary",
                eventId=event_id,
                body=event
            ).execute()

            print("Updated calendar event:", title)

        except Exception:
            calendar_service.events().insert(
                calendarId="primary",
                body=event
            ).execute()

            print("Added calendar event:", title)

        if assignment_id not in synced:
            task = {
                "title": title,
                "notes": "Gradescope link: " + a.get("link", "")
            }

            tasks_service.tasks().insert(
                tasklist="@default",
                body=task
            ).execute()

            print("Added task:", title)

            synced.append(assignment_id)
            save_synced(synced)
        else:
            print("Skipped task already synced:", title)

    print("Done syncing.")


if __name__ == "__main__":
    asyncio.run(main())