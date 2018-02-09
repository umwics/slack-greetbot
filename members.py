import datetime
import json
import os
import requests_cache
import slacker

default_img_url = "https://secure.gravatar.com"
active_threshold = datetime.timedelta(days=30)
today = datetime.datetime.today()
from_unix = datetime.datetime.fromtimestamp
slack = None
active_members = set()


def init():
    """Initial setup."""
    global slack
    if slack is None:
        slack = slacker.Slacker(
            os.environ["SLACK_TOKEN"],
            session=requests_cache.CachedSession(backend="memory"),
        )
        general = get_general()
        if general is None:
            return False
        fill_active_users(general)
        return bool(active_members)


def get_general():
    """Get the ID of #general."""
    response = slack.channels.list()
    if not response.successful:
        print("Couldn't list channels")
        return None

    if "channels" not in response.body:
        print("Missing 'channels' key")
        return None

    channels = response.body["channels"]
    for channel in channels:
        if channel["name"] == "general":
            return channel["id"]
    print("#general not found")
    return None


def fill_active_users(channel_id):
    """Fill the global active_members."""
    response = slack.channels.history(channel_id)
    if not response.successful:
        print("Couldn't get channel history")
        return

    if "messages" not in response.body:
        print("Missing 'messages' key")
        return

    messages = response.body["messages"]

    for m in messages:
        if m["type"] != "message":
            continue
        if m.get("subtype") == "channel_join":
            continue
        if from_unix(float(m["ts"])) - today > active_threshold:
            continue
        active_members.add(m["user"])


def member_filter(m):
    """Determine if we want to include member m."""
    bools = ["deleted", "is_bot", "is_restricted", "is_ultra_restricted"]
    return m["id"] in active_members and \
        not any(m[k] for k in bools) and m["id"] != "USLACKBOT"


def filter_fields(m):
    """Return a filtered version of member m."""
    m_filtered = {"name": m["real_name"]}

    no_img = m["profile"]["image_24"].startswith(default_img_url)
    for sz in [24, 32, 48, 72, 192, 512, 1024, "original"]:
        image = None if no_img else m["profile"].get("image_%s" % sz)
        m_filtered["image_%s" % sz] = image

    title = m["profile"]["title"]
    m_filtered["title"] = title if title else None

    return m_filtered


def finish(status, body):
    """Return the API response."""
    return {
        "isBase64Encoded": False,
        "headers": {},
        "statusCode": status,
        "body": body,
    }


def handler(event, context):
    """AWS Lambda entrypoint function."""
    try:
        if not init():
            print("Setup failed")
            finish(500, None)

        response = slack.users.list()
        if not response.successful:
            print("Failure retrieving members: %s" % response.error)
            return finish(500, None)
        elif "members" not in response.body:
            print("Missing 'members' key")
            return finish(500, None)

        members_raw = filter(member_filter, response.body["members"])
        members = [filter_fields(m) for m in members_raw]

    except Exception as e:
        print("Exception: %s" % e)
        return finish(500, None)

    return finish(200, json.dumps(members))
