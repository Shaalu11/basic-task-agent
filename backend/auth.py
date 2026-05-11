from fastapi import APIRouter
from google_auth_oauthlib.flow import Flow

router = APIRouter()

CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = "http://localhost:8000/auth"

# Store flow temporarily
flow_instance = None

@router.get("/login")
def login():
    global flow_instance

    flow_instance = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow_instance.authorization_url(prompt='consent')
    return {"auth_url": auth_url}