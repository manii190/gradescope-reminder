from playwright.sync_api import sync_playwright

LOGIN_FILE = "gradescope_login.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.gradescope.com/login")

    input("Log in to Gradescope, then press Enter here: ")

    context.storage_state(path=LOGIN_FILE)
    print("Login saved successfully!")

    browser.close()
