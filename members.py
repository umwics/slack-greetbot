import json
import os
import requests_cache
import slacker

default_img_url = "https://secure.gravatar.com"


def member_filter(m):
    """Determine if we want to include member m."""
    bools = ["deleted", "is_bot", "is_restricted", "is_ultra_restricted"]
    return not any(m[k] for k in bools) and m["id"] != "USLACKBOT"


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

    slack = slacker.Slacker(
        os.environ["SLACK_TOKEN"],
        session=requests_cache.CachedSession(),
    )
    try:
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
