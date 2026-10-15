import json
import os
import random
import time
import urllib.error
import urllib.request

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]  # e.g. @your_channel or -1001234567890
GH_TOKEN = os.environ["GH_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]  # owner/repo
OFFSET_VARIABLE = os.getenv("OFFSET_VARIABLE", "TELEGRAM_UPDATE_OFFSET")
REACTIONS = ["❤️", "🔥", "👍", "😍"]
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GH_API = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/variables/{OFFSET_VARIABLE}"

def request_json(url, method="GET", payload=None, headers=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            body = response.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e

def telegram(method, payload=None):
    result = request_json(f"{API}/{method}", "POST", payload,
                          {"Content-Type": "application/json"})
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")
    return result["result"]

def gh_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GH_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

def read_offset():
    try:
        data = request_json(GH_API, headers=gh_headers())
        return int(data.get("value", "0"))
    except RuntimeError as e:
        # Variable not created yet: start at the latest update, avoiding old posts.
        if "HTTP 404" in str(e):
            updates = telegram("getUpdates", {
                "timeout": 0, "allowed_updates": ["channel_post", "edited_channel_post"]
            })
            return (updates[-1]["update_id"] + 1) if updates else 0
        raise

def save_offset(offset):
    payload = {"name": OFFSET_VARIABLE, "value": str(offset)}
    try:
        request_json(GH_API, "PATCH", payload, gh_headers())
    except RuntimeError as e:
        if "HTTP 404" not in str(e):
            raise
        # Create the repository variable if it doesn't exist yet.
        create_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/variables"
        request_json(create_url, "POST", payload, gh_headers())

def main():
    # This workflow runs periodically, processes available channel posts, and exits.
    offset = read_offset()
    updates = telegram("getUpdates", {
        "offset": offset,
        "timeout": 20,
        "allowed_updates": ["channel_post"]
    })

    highest = offset - 1
    for update in updates:
        highest = max(highest, update["update_id"])
        post = update.get("channel_post")
        if not post:
            continue

        chat = post.get("chat", {})
        chat_id = chat.get("id")
        username = chat.get("username")
        expected = CHANNEL_ID.lstrip("@")
        is_target = str(chat_id) == CHANNEL_ID or (username and username.lower() == expected.lower())
        if not is_target:
            print(f"Skipping post from non-target channel: {chat.get('title', chat_id)}")
            continue

        message_id = post.get("message_id")
        reaction = random.choice(REACTIONS)
        try:
            telegram("setMessageReaction", {
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": [{"type": "emoji", "emoji": reaction}],
                "is_big": False
            })
            print(f"Reacted to channel post {message_id} with {reaction}")
        except Exception as e:
            # Do not silently claim success: show the API error in Actions logs.
            print(f"Could not react to post {message_id}: {e}")

    if updates and highest >= offset:
        save_offset(highest + 1)
    print(f"Done. Updates checked: {len(updates)}")

if __name__ == "__main__":
    main()
