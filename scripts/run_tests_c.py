
import argparse
import base64
import os
import time

import requests

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/v0"
#SUBMISSIONS_DIR = "/Volumes/znt-apfs/z-others/faculdade/fracoes/fracoes_py"
SUBMISSIONS_DIR = "/Volumes/znt-apfs/z-others/faculdade/G"
PROBLEM_ID = "aa916ed3-f232-4917-ada3-8305d1902d04"
LANGUAGE = "c"
POLL_INTERVAL_SECONDS = 2
MAX_POLL_ATTEMPTS = 30

# --- Helper Functions ---

def submit_code(source_path: str, token: str) -> str | None:
    """Reads a source file, encodes it, and submits it to the API."""
    print(f"Submitting {os.path.basename(source_path)}...")
    try:
        with open(source_path, "rb") as f:
            source_code_bytes = f.read()
    except IOError as e:
        print(f"  Error reading file: {e}")
        return None

    encoded_code = base64.b64encode(source_code_bytes).decode("utf-8")

    payload = {
        "problem_id": PROBLEM_ID,
        "language_type": LANGUAGE,
        "content": encoded_code,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/submissions", json=payload, headers=headers
        )
        response.raise_for_status()  # Raises an exception for 4xx/5xx errors
    except requests.exceptions.RequestException as e:
        print(f"  Error submitting to API: {e}")
        if e.response is not None:
            print(f"  Response body: {e.response.text}")
        return None

    submission_data = response.json()
    submission_id = submission_data.get("id")
    print(f"  Successfully submitted. Submission ID: {submission_id}")
    return submission_id


def poll_for_result(submission_id: str, token: str):
    """Polls the API for the result of a submission."""
    print(f"  Polling for result of submission {submission_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    attempts = 0
    while attempts < MAX_POLL_ATTEMPTS:
        try:
            response = requests.get(
                f"{API_BASE_URL}/submissions/{submission_id}", headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  Error polling API: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        result = response.json()
        status = result.get("status")

        if status not in ["IN_QUEUE", "PROCESSING"]:
            print(f"  Final status for {submission_id}: {status}")
            # Optionally print more details
            # print(f"  Result details: {result}")
            return

        time.sleep(POLL_INTERVAL_SECONDS)
        attempts += 1
    print(f"  Gave up polling for {submission_id} after {MAX_POLL_ATTEMPTS} attempts.")


def main():
    """Main function to run the submission and validation process."""
    parser = argparse.ArgumentParser(
        description="Submit and validate code submissions for the programming judge API."
    )
    parser.add_argument(
        "token", help="The JWT authentication token for the API."
    )
    args = parser.parse_args()

    print("--- Starting Submission Test ---")
    print(f"Target directory: {SUBMISSIONS_DIR}")

    for filename in sorted(os.listdir(SUBMISSIONS_DIR)):
        if filename.endswith(".c"):
            file_path = os.path.join(SUBMISSIONS_DIR, filename)
            submission_id = submit_code(file_path, args.token)
            if submission_id:
                poll_for_result(submission_id, args.token)
            print("-" * 20)

    print("--- Submission Test Finished ---")


if __name__ == "__main__":
    main()
