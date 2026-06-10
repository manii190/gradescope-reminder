import asyncio
import json
import os
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


def make_assignment_id(a):
    return a["course_short"] + "|" + a["name"] + "|" + a["due_date_raw"]


async def main():
    synced = load_synced()

    tasks_service = get_tasks_service()
    calendar_service = get_calendar_service()

    assignments = await get_all_assignments()

    for a in assignments:
        assignment_id = make_assignment_id(a)

        if assignment_id in synced:
            print("Skipped already synced:", a["name"])
            continue

        title = a["course_short"] + " — " + a["name"]

        task = {
            "title": title,
            "notes": "Gradescope link: " + a["link"]
        }

        tasks_service.tasks().insert(
            tasklist="@default",
            body=task
        ).execute()

        print("Added task:", title)

        event = {
            "summary": title,
            "description": "Gradescope link: " + a["link"],
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

        calendar_service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        print("Added calendar event:", title)

        synced.append(assignment_id)
        save_synced(synced)

    print("Done syncing.")


if __name__ == "__main__":
    asyncio.run(main())