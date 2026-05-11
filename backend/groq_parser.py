import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
import dateparser
import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TIME_RANGE_PATTERN = re.compile(
    r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))\s*(?:to|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))",
    re.I
)
SELF_PATTERN = re.compile(r"\b(myself|me|my email|self)\b", re.I)
DATE_WORD_PATTERN = re.compile(
    r"\b(today|tomorrow|tonight|tonite|next\s+\w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|on\s+\w+)\b",
    re.I
)


def has_explicit_date(text):
    return bool(DATE_WORD_PATTERN.search(text))


def normalize_time_string(value):
    parsed = dateparser.parse(value, settings={"PREFER_DATES_FROM": "future"})
    if not parsed:
        return None
    return parsed.strftime("%H:%M")


def extract_time_range(text):
    match = TIME_RANGE_PATTERN.search(text)
    if not match:
        return None, None

    start_time = normalize_time_string(match.group(1))
    end_time = normalize_time_string(match.group(2))

    return start_time, end_time


def parse_text(text):
    prompt = f"""
You are a smart AI assistant that extracts structured data.

RULES:

1. Detect correct action:
- "send email" → send_email
- "delete", "cancel" → delete
- "schedule", "add", time/date → add
- "what", "show", "schedule" → get_schedule

2. Understand dates:
- today
- tomorrow
- next monday / next friday
- specific dates

3. ALWAYS include:
- action
- title (if event)
- date_text (if relevant)
- time (HH:MM 24-hour)

4. For schedule queries:
- include "date_text"

Examples:

"meeting tomorrow at 10am"
{{"action":"add","title":"Meeting","date_text":"tomorrow","time":"10:00"}}

"what's my schedule tomorrow"
{{"action":"get_schedule","date_text":"tomorrow"}}

"delete meeting"
{{"action":"delete","title":"Meeting"}}

"send email to john@gmail.com saying meeting postponed"
{{"action":"send_email","to":"john@gmail.com","subject":"Meeting Update","body":"meeting postponed"}}


Return ONLY JSON.

Sentence: {text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    reply = response.choices[0].message.content
    print("RAW AI:", reply)

    match = re.search(r'\{.*\}', reply, re.DOTALL)

    if not match:
        return {"action": "error", "message": "Could not understand input"}

    try:
        data = json.loads(match.group())
    except:
        return {"action": "error", "message": "Invalid AI response"}

    if "date_text" in data:
        if data["date_text"].strip().lower() == "today" and not has_explicit_date(text):
            data.pop("date_text", None)
        else:
            parsed_date = dateparser.parse(
                data["date_text"],
                settings={"PREFER_DATES_FROM": "future"}
            )
            if parsed_date:
                data["date"] = parsed_date.strftime("%Y-%m-%d")

    # Extract explicit time range from the text when present
    if data.get("action") == "add":
        start_time, end_time = extract_time_range(text)
        if start_time and end_time:
            data["time"] = start_time
            data["end_time"] = end_time

    # Interpret self-email instructions
    if data.get("action") == "send_email":
        if not data.get("to") or SELF_PATTERN.search(text):
            data["to"] = None

    # Default time for scheduling if none found
    if data.get("action") == "add" and not data.get("time"):
        data["time"] = "09:00"

    return data