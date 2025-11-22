import argparse
import base64
import os
import time

import requests

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/v0"
# SUBMISSIONS_DIR = "/Users/zanetti/projetos/boca_scrapping/ordered-by-problem"
# SUBMISSIONS_DIR = "/Users/zanetti/projetos/boca_scrapping/ordered-by-problem"
SUBMISSIONS_DIR = "/Users/zanetti/projetos/tcc_api/scripts/testes-outras-linguagens"
POLL_INTERVAL_SECONDS = 2
MAX_POLL_ATTEMPTS = 30

PROBLEM_ID_BY_PATH_NAME = {
    "A": "abad3db3-0f6a-4834-88e0-fd7ca0f42470",
    # "B": "d2a2c3f9-f9b9-4e86-8dc1-4c701adf03ab",
    # "C": "e28acc7a-3a3f-4dd3-a62f-2ce3e4fbe969",
    # "D": "e60eaa81-8d6f-4a7f-8f51-35e1a52d80f8",
    # "E": "7fe6335d-a4f0-44df-b871-941ddf9dc591",
    # "F": "b3dec5ab-8467-4fe8-a33d-ed5e3c2215ae",
    # "G": "2fabf551-6e9d-49f6-aa24-52b35a290393",
    # "H": "f48d15c0-9c8a-4e88-a0e6-9e525bf5be67",
    # "I": "b3bd0435-d056-4a13-b418-6e8dc58820d1",
    # "J": "7d68ca63-99ae-43fb-86b2-ea7e86b7440e",
}

# --- Helper Functions ---

def submit_code(source_path: str, token: str, language_type: str, problem_id: str) -> str | None:
    """Reads a source file, encodes it, and submits it to the API."""
    print(f"Submitting {os.path.basename(source_path)} for problem {problem_id}...")
    try:
        with open(source_path, "rb") as f:
            source_code_bytes = f.read()
    except IOError as e:
        print(f"  Error reading file: {e}")
        return None

    encoded_code = base64.b64encode(source_code_bytes).decode("utf-8")
    
    payload = {
        "problem_id": problem_id,
        "language_type": language_type,
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
    print(f"Base submissions directory: {SUBMISSIONS_DIR}")

    for path_name, problem_id in PROBLEM_ID_BY_PATH_NAME.items():
        problem_dir = os.path.join(SUBMISSIONS_DIR, path_name)
        print(f"\n--- Processing directory: {problem_dir} ---")

        if not os.path.isdir(problem_dir):
            print(f"  Directory not found, skipping.")
            continue

        for filename in sorted(os.listdir(problem_dir)):
            # Simple extension check, can be improved
            if not any(filename.endswith(ext) for ext in [".c", ".cpp", ".cs", ".py", ".js", ".java", ".go", ".php"]):
                continue

            file_path = os.path.join(problem_dir, filename)
            language_type = filename.rsplit(".", 1)[1]
            
            submission_id = submit_code(file_path, args.token, language_type, problem_id)
            if submission_id:
                poll_for_result(submission_id, args.token)
            print("-" * 20)

    print("--- Submission Test Finished ---")


if __name__ == "__main__":
    main()