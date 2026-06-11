"""
Phase 4: Read Open Assignments
- Opens each course one by one
- Reads only assignments that are open / No Submission
- Ignores completed/submitted assignments
"""

import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright
from config import SESSION_FILE, GRADESCOPE_URL
from courses import get_all_courses

async def get_assignments_for_course(page, course):
    assignments = []

    await page.goto(course["url"])
    await page.wait_for_timeout(5000)

    rows = page.locator("tr")
    count = await rows.count()

    for i in range(count):
        row = rows.nth(i)
        row_text = (await row.inner_text()).strip()

        if "No Submission" not in row_text:
            continue

        parts = row_text.split("\n")

        name = parts[0].strip()
        due_date_raw = parts[-1].strip()

        link_el = row.locator("a").first
        link = course["url"]

        if await link_el.count() > 0:
            href = await link_el.get_attribute("href")
            if href:
                if href.startswith("http"):
                    link = href
                else:
                    link = GRADESCOPE_URL.rstrip("/") + href

        if await link_el.count() > 0:
            href = await link_el.first.get_attribute("href")
            if href:
                link = href if href.startswith("http") else GRADESCOPE_URL + href

        course_name = course.get("short_name", course.get("name", "Course"))

        assignments.append({
            "course_short": course_name,
            "course_full": course.get("full_name", ""),
            "course_url": course["url"],
            "name": name,
            "due_date_raw": due_date_raw,
            "due_date_iso": parse_due_date(due_date_raw),
            "link": link,
            "status": "No Submission",
        })

    return assignments



def parse_due_date(raw):
    if not raw:
        return ""

    raw = raw.strip()

    if re.match(r"\d{4}-\d{2}-\d{2}T", raw):
        return raw

    formats = [
        "%b %d at %I:%M%p",
        "%B %d, %Y %I:%M %p",
        "%b %d, %Y %I:%M %p",
        "%b %d %I:%M%p",
    ]

    for fmt in formats:
        try:
            if "%Y" not in fmt:
                test = raw + " " + str(datetime.now().year)
                dt = datetime.strptime(test, fmt + " %Y")
            else:
                dt = datetime.strptime(raw, fmt)

            return dt.strftime("%Y-%m-%dT%H:%M:%S")

        except ValueError:
            pass

    return raw


async def get_all_assignments():
    courses = await get_all_courses()

    if not courses:
        return []

    print()
    print("📋 Reading open assignments from each course...")

    all_assignments = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=SESSION_FILE)
        page = await context.new_page()

        for course in courses:
            course_name = course.get("short_name", course.get("name", "Course"))

            print(f"   Opening {course_name}...")

            try:
                assignments = await get_assignments_for_course(page, course)
                all_assignments.extend(assignments)
                print(f"   ✅ {len(assignments)} open assignment(s) found")

            except Exception as e:
                print(f"   ⚠️ Could not read {course_name}: {e}")

        await browser.close()

    print()
    print(f"📦 Total open assignments found: {len(all_assignments)}")
    print()

    for a in all_assignments:
        due = a["due_date_raw"] or "No due date"

        print(f"   {a['course_short']} — {a['name']}")
        print(f"     Due: {due}")
        print(f"     Status: {a['status']}")
        print(f"     Link: {a['link']}")
        print()

    return all_assignments


if __name__ == "__main__":
    asyncio.run(get_all_assignments())