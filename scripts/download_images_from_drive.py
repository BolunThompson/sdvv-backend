#!/usr/bin/env python3
# Large amounts taken from here
# https://github.com/gsuitedevs/python-samples/blob/master/drive/quickstart/quickstart.py
# Secret "credentials.json" not included
# NOTE: Is there a way to avoid using a personal account for google drive api access?

import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FOLDER_ID = "1jofuld9MEwRr2ZpQjBD2YZZ0tRTCv7xE"
DOWNLOAD_DIRECTOTY = "../downloads/images/"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def recursive_file_ids(folder_id, drive_service):
    """
    Returns a list of tuples formattied (name, id) excluding folders.
    When a nested folder is found, includes the contents of it.
    """
    file_ids = []
    page_token = None
    while True:
        response = (
            drive_service.files()
            .list(
                q="'{}' in parents".format(folder_id),
                spaces="drive",
                fields="nextPageToken, files(name, id, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        for file in response["files"]:
            if file["mimeType"] == "application/vnd.google-apps.folder":
                file_ids.extend(recursive_file_ids(file["id"], drive_service))
            else:
                file_ids.append((file["name"], file["id"]))
        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break
    return file_ids


def credentials(automated):
    """
    Gets the credentials for google drive.
    If none can be found, requests a google login if automated is False,
    and errors if it is True.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif automated:
            text = "There are no valid credentials in the token.pickle file."
            raise RuntimeError(text)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8000)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds


def download_folder_contents(folder_id, download_directory, credentials):
    drive_service = build("drive", "v3", credentials=credentials)
    ids = recursive_file_ids(folder_id, drive_service)
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    for file_id in ids:
        request = drive_service.files().get_media(fileId=file_id[1])
        with open(download_directory + file_id[0], mode="wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                done = downloader.next_chunk()[1]


if __name__ == "__main__":
    download_folder_contents(FOLDER_ID, DOWNLOAD_DIRECTOTY, credentials(automated=True))
