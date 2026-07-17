import asyncio
import json
from courses import get_all_courses

async def main():
    courses = await get_all_courses()

    course_data = []

    for i, c in enumerate(courses):
        raw_name = c.get("name", "")
        lines = raw_name.split("\n")

        course_data.append({
            "id": str(i + 1),
            "code": lines[0] if len(lines) > 0 else "Course",
            "name": lines[1] if len(lines) > 1 else raw_name,
            "assignmentCount": lines[2] if len(lines) > 2 else "",
            "url": c.get("url", "")
        })

    with open("courses_export.json", "w") as f:
        json.dump(course_data, f, indent=2)

asyncio.run(main())