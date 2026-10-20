import json
reply_data = [
    {
        "comment_id": "6295641899",
        "reply": "Understood. Acknowledging that this work is now obsolete and stopping work on this task."
    }
]
with open('reply.json', 'w') as f:
    json.dump(reply_data, f)
