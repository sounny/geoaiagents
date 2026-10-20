import json

def get_replies():
    replies = [
        {
            "comment_id": "6292740903",
            "reply": "Understood. Acknowledging that this work has unresolvable merge conflicts and the PR is being closed. Stopping work on this task."
        }
    ]
    return json.dumps(replies)

print(get_replies())
