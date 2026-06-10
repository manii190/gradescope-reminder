from googleapiclient.discovery import build
from google_auth import get_google_creds

def get_calendar_service():
    creds = get_google_creds()
    return build("calendar", "v3", credentials=creds)