from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        storage_state="gradescope_login.json"
    )

    page = context.new_page()

    page.goto("https://www.gradescope.com/account")

    page.wait_for_timeout(5000)

    print(page.title())

    input("Press Enter to close...")

    browser.close()
