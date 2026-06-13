import asyncio
import json
from assignments import get_all_assignments

async def main():
    assignments = await get_all_assignments()

    dashboard_data = []

    for i, a in enumerate(assignments):
        dashboard_data.append({
            "id": str(i + 1),
            "title": a["name"],
            "course": a["course_short"],
            "dueDate": a["due_date_raw"],
            "dueDateIso": a["due_date_iso"],
            "status": "submitted" if a["status"] == "Submitted" else "upcoming",
            "calendarSynced": True,
            "link": a["link"]
        })

    with open("assignments_export.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)

asyncio.run(main())