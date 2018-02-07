import os
import slacker

if __name__ == "__main__":
    if "SLACK_TOKEN" not in os.environ:
        print("Set SLACK_TOKEN environment variable")
        exit(1)

    slack = slacker.Slacker(os.environ["SLACK_TOKEN"])
    users_resp = slack.users.list().body
    users = users_resp["members"]

    print("There are %d users." % len(users))
