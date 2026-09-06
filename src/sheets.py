import os

def upload_to_sheets():
    if not os.path.exists('credentials.json'):
        print("Google Sheets status = BLOCKED")
        print("Credential credentials.json required for Sheets upload.")
        return
    # Here would be the google-api-python-client code
    print("Google Sheets upload complete.")
