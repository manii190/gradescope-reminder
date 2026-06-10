import asyncio
from playwright.async_api import async_playwright
from config import SESSION_FILE, GRADESCOPE_URL


SEMESTER_WORDS = ["Spring", "Summer", "Fall", "Winter"]


def is_semester(line):
    return any(line.startswith(word) for word in SEMESTER_WORDS) and any(ch.isdigit() for ch in line)


async def get_all_courses():
    print("📚 Reading current semester courses from Gradescope...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=SESSION_FILE)
        page = await context.new_page()

        await page.goto(f"{GRADESCOPE_URL}/account")
        await page.wait_for_timeout(5000)

        body = await page.locator("body").inner_text()
        lines = [line.strip() for line in body.split("\n") if line.strip()]

        current_term = ""
        course_names = []

        collecting = False

        for line in lines:
            if is_semester(line):
                if not collecting:
                    current_term = line
                    collecting = True
                    continue
                else:
                    break

            if collecting:
                if line.endswith("assignments"):
                    continue
                if line == "Add a course":
                    continue
                if line.startswith("CSC ") or line.startswith("MATH ") or line.startswith("Math"):
                    course_names.append(line)

        links = page.locator("a[href*='/courses/']")
        count = await links.count()

        courses = []

        for i in range(count):
            link = links.nth(i)
            text = (await link.inner_text()).strip()
            href = await link.get_attribute("href")

            for name in course_names:
                if name in text and "\n" in text:
                    if not href.startswith("http"):
                        href = GRADESCOPE_URL + href

                    if href not in [c["url"] for c in courses]:
                        courses.append({
                            "name": text,
                            "url": href
                        })

        await browser.close()

    print("Current semester:", current_term)
    print(f"✅ Found {len(courses)} current course(s):")

    for c in courses:
        print(c["name"])
        print(c["url"])
        print("-----")

    return courses


if __name__ == "__main__":
    asyncio.run(get_all_courses())