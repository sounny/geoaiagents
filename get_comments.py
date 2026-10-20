import json

def main():
    try:
        from test_dd2dms import format_dms
    except ImportError:
        pass

    print("No way to read the truncated comments, I will retry the tool")

if __name__ == "__main__":
    main()
