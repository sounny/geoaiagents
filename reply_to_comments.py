import os
import sys

def reply_to_pr_comments(replies):
    print("Calling reply_to_pr_comments tool with:")
    print(replies)

if __name__ == "__main__":
    reply_to_pr_comments(sys.argv[1])
