import json

replies = [
    {
        "comment_id": "6346207150",
        "reply": "Understood. Acknowledging that this PR is being closed and this work is now obsolete. Stopping work on this task."
    }
]
with open('replies.json', 'w') as f:
    json.dump(replies, f)
