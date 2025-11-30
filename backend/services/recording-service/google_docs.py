import json
import os
from typing import Optional, Tuple

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


def _load_service_account_info() -> dict:
    raw_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_INFO")
    if raw_info:
        return json.loads(raw_info)

    info_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if info_path and os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    raise RuntimeError("Google service account credentials are not configured")


def _build_services():
    credentials_info = _load_service_account_info()
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    )
    docs_service = build("docs", "v1", credentials=credentials, cache_discovery=False)
    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    return docs_service, drive_service


_docs_service, _drive_service = _build_services()


def create_document(title: str, summary: Optional[str]) -> Tuple[str, str]:
    try:
        doc = _docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        if summary:
            _docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {
                            "insertText": {
                                "location": {"index": 1},
                                "text": summary,
                            }
                        }
                    ]
                },
            ).execute()

        _drive_service.permissions().create(
            fileId=doc_id,
            body={"role": "reader", "type": "anyone"},
            fields="id",
        ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        return doc_id, doc_url

    except (HttpError, GoogleAuthError) as exc:
        raise RuntimeError(f"failed to create google doc: {exc}") from exc

