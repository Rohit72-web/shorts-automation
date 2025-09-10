import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secret.json"  # Path to your OAuth2 credentials

def upload_video(file_path, title, description, category="22", privacy="public"):
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "categoryId": category,
            "title": title,
            "description": description,
        },
        "status": {
            "privacyStatus": privacy,
        }
    }

    media = googleapiclient.http.MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print("✅ Video uploaded! Video ID:", response["id"])

if __name__ == "__main__":
    upload_video(
        file_path="final_news_video.mp4",
        title="Latest Indian News Shorts",
        description="Auto-generated news shorts video."
    )