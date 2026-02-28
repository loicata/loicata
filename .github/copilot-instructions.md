<!-- Copilot instructions for loicata/loicata repo -->
# Copilot instructions

This repository is a single-script Python utility for checking the host's public IP against AbuseIPDB and logging the results.

- **Entry point:** `IP_scan.py` — a scheduled CLI script that:
  - detects public IP via `requests.get("https://api.ipify.org")`;
  - queries AbuseIPDB in `check_ip_reputation()` (endpoint: `https://api.abuseipdb.com/api/v2/check`);
  - writes human-readable output to `IP_scan_log.txt` (or a user-selected path via `tkinter`).

- **Key functions & behavior (explicit examples):**
  - `check_ip_reputation(ip_address, api_key)` — performs the AbuseIPDB HTTP request and returns JSON or `{"error": ...}` on failure.
  - `log_result(file_path, ip_address, result)` — appends a timestamped block to the log file using fields from `result['data']`.
  - `run_scan(file_path)` — obtains public IP, calls `check_ip_reputation`, prints human-readable output, and calls `log_result()`.
  - `main()` — ensures `IP_scan_log.txt` exists (offers a `tkinter` save dialog if available), runs one immediate scan, then schedules daily runs with `schedule.every().day.at("01:00").do(run_scan, file_path=file_path)`.

- **Dependencies & install notes (how to run locally):**
  - Required Python packages used: `requests`, `schedule` (the script auto-installs `schedule` if missing). `tkinter` is optional and the script attempts `pip install tk` if not present.
  - Run locally: `python IP_scan.py` (script will run once immediately and then enter the scheduler loop).
  - To install manually: `pip install requests schedule` (Windows usually ships `tkinter` with the official Python installer).

- **Integration & external services:**
  - AbuseIPDB API (requires a key). The current `IP_scan.py` contains a hard-coded `api_key` string — treat this as sensitive; prefer using an env var when modifying the code.

- **Project conventions & patterns to follow when editing:**
  - Single-file utility: prefer small, contained edits in `IP_scan.py` rather than adding multiple modules unless expanding scope.
  - Logging pattern: append-only human-readable blocks written by `log_result()`; preserve this format for backward compatibility.
  - Scheduling: the project uses `schedule` with a blocking `while True` loop and `time.sleep(60)`; keep scheduling behavior consistent unless explicitly changing runtime model.

- **Where to change behavior:**
  - Change log file name/location: `file_path` variable in `main()` and `select_save_location()`.
  - Change AbuseIPDB usage: update `check_ip_reputation()` and `api_key` handling.
  - To run one-off scans in tests, call `run_scan(file_path)` directly (mock `requests.get` and `check_ip_reputation()` responses when unit-testing).

- **Debugging tips specific to this repo:**
  - The script prints detailed results and errors to stdout; run `python IP_scan.py` interactively to reproduce issues.
  - If `tkinter` file dialog fails on Windows, the script falls back to creating `IP_scan_log.txt` in the current directory.
  - Network failures surface as `{"error": ...}` from `check_ip_reputation()` — inspect `response.content` in that function when debugging API responses.

If anything here is unclear or you'd like me to document additional file-level examples or a recommended env-var pattern for the API key, tell me which areas to expand.
