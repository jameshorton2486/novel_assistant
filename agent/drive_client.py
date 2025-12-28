import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


# ----------------------------------------------------------
# Google Drive API Setup
# ----------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

CREDENTIALS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "credentials", "credentials.json"
)

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")


class DriveClient:
    """
    Handles Google Drive OAuth authentication and file operations.
    Creates and manages:
        NovelAssistant/
            Chapters/
            Notes/
            Characters/
    """

    def __init__(self):
        self.service = self.authenticate()
        self.root_folder_id = self.get_or_create_folder("NovelAssistant")
        self.chapters_folder = self.get_or_create_subfolder(self.root_folder_id, "Chapters")
        self.notes_folder = self.get_or_create_subfolder(self.root_folder_id, "Notes")
        self.characters_folder = self.get_or_create_subfolder(self.root_folder_id, "Characters")

    # ------------------------------------------------------
    # AUTHENTICATION
    # ------------------------------------------------------
    def authenticate(self):
        """
        Handles OAuth login flow.
        Creates token.json after first login.
        """

        creds = None

        # Load cached token
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        # Refresh or create new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        "Missing credentials.json in /credentials folder."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        return build("drive", "v3", credentials=creds)

    # ------------------------------------------------------
    # FOLDER HELPERS
    # ------------------------------------------------------
    def get_or_create_folder(self, folder_name):
        """
        Returns the folder ID, or creates it if missing.
        """

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        results = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )

        items = results.get("files", [])

        if items:
            return items[0]["id"]

        # Create folder
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        folder = self.service.files().create(body=file_metadata, fields="id").execute()
        return folder["id"]

    def get_or_create_subfolder(self, parent_id, subfolder_name):
        """
        Creates subfolders inside NovelAssistant folder.
        """

        query = (
            f"name='{subfolder_name}' and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"'{parent_id}' in parents and trashed=false"
        )

        results = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )

        items = results.get("files", [])

        if items:
            return items[0]["id"]

        # Create subfolder
        metadata = {
            "name": subfolder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }

        folder = self.service.files().create(body=metadata, fields="id").execute()
        return folder["id"]

    # ------------------------------------------------------
    # FILE OPERATIONS
    # ------------------------------------------------------
    def save_text_file(self, folder_id, filename, text):
        """
        Saves a plain text file to Google Drive.
        """
        file_metadata = {
            "name": filename,
            "parents": [folder_id],
            "mimeType": "text/plain",
        }

        stream = io.BytesIO(text.encode("utf-8"))
        media = MediaIoBaseUpload(stream, mimetype="text/plain")

        # Check if file exists → update instead of duplicate
        file_id = self.find_file_in_folder(folder_id, filename)

        if file_id:
            # Update
            self.service.files().update(
                fileId=file_id, body=file_metadata, media_body=media
            ).execute()
        else:
            # Create new
            self.service.files().create(
                body=file_metadata, media_body=media
            ).execute()

        return True

    def load_text_file(self, folder_id, filename):
        """
        Loads and returns a text file from Google Drive.
        """

        file_id = self.find_file_in_folder(folder_id, filename)
        if not file_id:
            return None

        request = self.service.files().get_media(fileId=file_id)
        stream = io.BytesIO()
        downloader = MediaIoBaseDownload(stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        return stream.getvalue().decode("utf-8")

    def list_files(self, folder_id):
        """
        Returns a list of filenames inside a folder.
        """

        query = f"'{folder_id}' in parents and mimeType='text/plain' and trashed=false"

        results = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )

        return [file["name"] for file in results.get("files", [])]

    def find_file_in_folder(self, folder_id, filename):
        """
        Returns file ID if the file exists.
        """

        query = (
            f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        )

        results = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )

        items = results.get("files", [])
        return items[0]["id"] if items else None
