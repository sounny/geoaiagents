
import json

def reply_to_pr_comments(replies):
    print("replying with:")
    print(replies)

reply_to_pr_comments(
    replies='''[
        {
            "comment_id": "6294480389",
            "reply": "Understood. Acknowledging that this work is now obsolete due to merge conflicts and stopping work on this task."
        }
    ]'''
)
