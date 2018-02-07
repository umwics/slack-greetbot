import json
import os
import slacker

default_img_url = "https://secure.gravatar.com"


def member_filter(m):
    """Determine if we want to include member m."""
    return not any(
        m[k] for k in
        ["deleted", "is_bot", "is_restricted", "is_ultra_restricted"]
    )


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


def handler(event, context):
    """AWS Lambda entrypoint function."""
    status = 200

    try:
        slack = slacker.Slacker(os.environ["SLACK_TOKEN"])
        members_raw = filter(member_filter, slack.users.list().body["members"])
        members = [filter_fields(m) for m in members_raw]

    except Exception as e:
        print("Exception: %s" % e)
        status = 500

    return {
        "isBase64Encoded": False,
        "headers": {},
        "statusCode": status,
        "body": json.dumps(members),
    }
