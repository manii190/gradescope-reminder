from googleapiclient.discovery import build
from google_auth import get_google_creds

def get_tasks_service():
    creds = get_google_creds()
    return build("tasks", "v1", credentials=creds)