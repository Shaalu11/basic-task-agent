from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from token_store import save_token, load_token, delete_token
from groq_parser import parse_text
from calendar_service import add_event, delete_event, reschedule_event
from gmail_service import send_email

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

import dateparser
from datetime import timedelta
import pytz
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]
REDIRECT_URI = "http://localhost:8000/auth"

flow_instance = None


# ✅ TOKEN VALIDATION
def is_token_valid(email, token):
    try:
        creds = Credentials.from_authorized_user_info(token)

        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())

            new_token = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }

            save_token(email, new_token)
            return True

        return not creds.expired

    except Exception as e:
        print("TOKEN ERROR:", e)
        return False


def get_today_date_if_future(time_str):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    parsed = dateparser.parse(
        time_str,
        settings={
            "RELATIVE_BASE": now,
            "PREFER_DATES_FROM": "future"
        }
    )
    if not parsed:
        return None

    if parsed.date() == now.date():
        return now.strftime("%Y-%m-%d")

    return None


def is_datetime_in_past(date_str, time_str):
    if not date_str or not time_str:
        return False

    try:
        ist = pytz.timezone("Asia/Kolkata")
        parsed_time = dateparser.parse(time_str, settings={"PREFER_DATES_FROM": "future"})
        if not parsed_time:
            return False

        formatted_time = parsed_time.strftime("%H:%M")
        event_dt = datetime.datetime.strptime(f"{date_str} {formatted_time}", "%Y-%m-%d %H:%M")
        event_dt = ist.localize(event_dt)
        return event_dt <= datetime.datetime.now(ist)
    except Exception:
        return False


@app.get("/")
def home():
    return {"message": "AI Task Agent Running"}


# ✅ LOGIN
@app.get("/login")
def login():
    global flow_instance

    flow_instance = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, _ = flow_instance.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    return {"auth_url": authorization_url}


# ✅ AUTH CALLBACK
@app.get("/auth")
async def auth(request: Request):
    global flow_instance

    code = request.query_params.get("code")

    if not flow_instance:
        return {"error": "Login session expired. Try again."}

    flow_instance.fetch_token(code=code)
    creds = flow_instance.credentials

    token = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    email = user_info['email']

    save_token(email, token)

    return RedirectResponse(f"http://localhost:3000/?email={email}")


# ✅ LOGOUT
@app.post("/logout")
async def logout(data: dict):
    email = data.get("email")
    if not email:
        return {"error": "Email missing"}
    
    delete_token(email)
    return {"success": True, "message": "Logged out successfully"}


# ✅ VALIDATE SESSION
@app.post("/validate-session")
async def validate_session(data: dict):
    email = data.get("email")
    if not email:
        return {"error": "Email missing"}
    
    token = load_token(email)
    
    if not token:
        return {"valid": False}
    
    if is_token_valid(email, token):
        return {"valid": True}
    else:
        delete_token(email)
        return {"valid": False}


# ✅ GET EVENTS
@app.get("/events/{email}")
async def get_events(email: str):
    try:
        if not email:
            return {"error": "Email missing"}

        token = load_token(email)

        if not token:
            return {"error": "User not authenticated"}

        if not is_token_valid(email, token):
            return {"error": "Session expired"}

        service = build(
            'calendar',
            'v3',
            credentials=Credentials.from_authorized_user_info(token)
        )

        # Get events for the next 30 days and past 30 days
        now = datetime.datetime.utcnow()
        start_date = now - datetime.timedelta(days=30)
        end_date = now + datetime.timedelta(days=30)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events

    except Exception as e:
        print("GET EVENTS ERROR:", str(e))
        return {"error": str(e)}


# ✅ DELETE EVENT BY ID
@app.delete("/events/{email}/{event_id}")
async def delete_event_by_id(email: str, event_id: str):
    try:
        if not email:
            return {"error": "Email missing"}

        token = load_token(email)

        if not token:
            return {"error": "User not authenticated"}

        if not is_token_valid(email, token):
            return {"error": "Session expired"}

        service = build(
            'calendar',
            'v3',
            credentials=Credentials.from_authorized_user_info(token)
        )

        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()

        return {"message": "Event deleted successfully"}

    except Exception as e:
        print("DELETE EVENT ERROR:", str(e))
        return {"error": str(e)}


# ✅ AI TASK
@app.post("/ai-task")
async def ai_task(data: dict):
    try:
        text = data.get("text")
        email = data.get("email")

        print("INPUT:", text)

        if not email:
            return {"error": "Email missing"}

        token = load_token(email)

        if not token:
            return {"error": "User not authenticated"}

        if not is_token_valid(email, token):
            return {"error": "Session expired"}

        parsed = parse_text(text)

        print("PARSED:", parsed)

        if parsed.get("action") == "error":
            return {"message": parsed.get("message")}

        # 🔥 EMAIL
        if parsed.get("action") == "send_email":
            to_email = parsed.get("to")
            if not to_email:
                to_email = email

            return send_email(
                token,
                to_email,
                parsed.get("subject", "Message"),
                parsed.get("body"),
                email
            )

        # ✅ ADD
        elif parsed.get("action") == "add":
            title = parsed.get("title") or text.split(" at ")[0]
            date = parsed.get("date")
            time_value = parsed.get("time")

            if not date:
                date = get_today_date_if_future(time_value)
                if not date:
                    return {"error": "Time has already passed today. Please specify a date."}

            if is_datetime_in_past(date, time_value):
                return {"error": "Time has already passed today. Please specify a date."}

            return add_event(
                token,
                title,
                date,
                time_value,
                parsed.get("end_time")
            )

        # ✅ DELETE
        elif parsed.get("action") == "delete":
            return delete_event(token, parsed.get("title"))

        # 🔥 RESCHEDULE
        elif parsed.get("action") == "reschedule":
            return reschedule_event(
                token,
                parsed.get("title"),
                parsed.get("date"),
                parsed.get("time")
            )

        # ✅ SCHEDULE
        elif parsed.get("action") == "get_schedule":
            date_text = parsed.get("date_text", "today")

            parsed_date = dateparser.parse(date_text)

            ist = pytz.timezone("Asia/Kolkata")

            start = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start = ist.localize(start)

            end = start + timedelta(days=1)

            service = build(
                'calendar',
                'v3',
                credentials=Credentials.from_authorized_user_info(token)
            )

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return {"message": f"No events on {date_text}"}

            msg = f"Schedule for {date_text}:\n"
            for e in events:
                msg += f"{e['start']['dateTime'][11:16]} - {e['summary']}\n"

            return {"message": msg}

        return {"message": "Unknown action"}

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}