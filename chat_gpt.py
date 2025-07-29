import os
import json
import time
from dotenv import load_dotenv
import openai

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Paths ===
ASSISTANT_PATH = "Settings/assistant.json"
STATE_PATH = "Settings/gpt_state.json"

# === Load assistant info ===
with open(ASSISTANT_PATH, "r", encoding="utf-8") as f:
    assistant = json.load(f)
ASSISTANT_ID = assistant["id"]

# === Load or init state ===
if os.path.exists(STATE_PATH):
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)
else:
    state = {
        "thread_id": None,
        "file_paths": [],
        "file_id_list": {}
    }

def save_state():
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def ensure_file_uploaded(client, file_path):
    if file_path in state["file_id_list"] and state["file_id_list"][file_path]:
        return state["file_id_list"][file_path]

    with open(file_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
        state["file_id_list"][file_path] = uploaded.id
        save_state()
        return uploaded.id

def ensure_thread(client):
    if state.get("thread_id"):
        return state["thread_id"]
    thread = client.beta.threads.create()
    state["thread_id"] = thread.id
    save_state()
    return thread.id

def chat_gpt(email_text: str):
    client = openai.Client()

    file_paths = state.get("file_paths", [])
    file_ids = [ensure_file_uploaded(client, path) for path in file_paths]

    thread_id = ensure_thread(client)
    attachments = [
        {"file_id": fid, "tools": [{"type": "file_search"}]}
        for fid in file_ids
    ]
    # Add user message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"Reply to the following email(1. Use language corresponding to the email! 2. File attachments of e-mail might not be visible to you, but assume contents):\n\n{email_text}",
        attachments=attachments
    )

    # Run assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    # Wait for completion
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            raise RuntimeError("GPT run failed.")
        time.sleep(1)

    # Fetch response
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages.data:
        if msg.role == "assistant" and msg.run_id == run.id:
            return msg.content[0].text.value

    return "[No assistant reply found.]"
