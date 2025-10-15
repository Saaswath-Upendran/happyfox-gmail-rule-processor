from __future__ import annotations
import logging
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .config import settings
import os

logger = logging.getLogger(__name__)


SCOPES = [
"https://www.googleapis.com/auth/gmail.readonly",
"https://www.googleapis.com/auth/gmail.modify",
]


class GmailClient:
    def __init__(self):
        self.creds: Optional[Credentials] = None
        self.service = None


    def authenticate(self) -> None:
        logger.info("Starting OAuth authentication")
        creds = None
        if settings.google_token_path and os.path.exists(settings.google_token_path):
            creds = Credentials.from_authorized_user_file(settings.google_token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(settings.google_credentials_path, SCOPES)
                flow.redirect_uri = 'http://localhost:5000/'
                creds = flow.run_local_server(port=5000)
            with open(settings.google_token_path, "w") as token:
                token.write(creds.to_json())
        self.creds = creds
        self.service = build("gmail", "v1", credentials=creds)
        logger.info("OAuth complete; service initialized")


    def list_message_ids(self, max_results: int = 100) -> List[str]:
        res = self.service.users().messages().list(userId="me", maxResults=max_results, labelIds=["INBOX"]).execute()
        return [m["id"] for m in res.get("messages", [])]


    def get_message(self, msg_id: str) -> Dict[str, Any]:
        return self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    def get_label_id(self, name: str) -> str:
        """Return Gmail label ID for name, creating it if missing."""
        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        for lbl in labels:
            if lbl["name"].lower() == name.lower():
                return lbl["id"]

        # If not found, create it
        body = {"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        new_lbl = self.service.users().labels().create(userId="me", body=body).execute()
        return new_lbl["id"]

    def modify_message_labels(self, msg_id: str, add: List[str] | None = None, remove: List[str] | None = None) -> Dict[str, Any]:
        body = {"addLabelIds": add or [], "removeLabelIds": remove or []}
        return self.service.users().messages().modify(userId="me", id=msg_id, body=body).execute()
