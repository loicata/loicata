import requests
from datetime import datetime
import time
import os
import sys
import importlib.util
import subprocess

def is_package_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

# Check and install 'schedule' if needed
if not is_package_installed("schedule"):
    print("Installing 'schedule' module...")
    if not install_package("schedule"):
        print("Failed to install 'schedule'. Please install it manually with: pip install schedule")
        sys.exit(1)
import schedule

def is_tkinter_installed():
    return importlib.util.find_spec("tkinter") is not None

def install_tkinter():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
        return True
    except subprocess.CalledProcessError:
        return False

def read_api_key():
    try:
        with open("IP_scan_api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: The file 'IP_scan_api_key.txt' was not found in the current directory.")
        return None
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

def check_ip_reputation(ip_address, api_key):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": "90"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def select_save_location():
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("Error: tkinter is not available. Unable to open file selection window.")
        return None

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".log",
        initialfile="IP_scan",
        title="Create IP_scan.log file",
        filetypes=[("Log files", "*.log"), ("All files", "*.*")]
    )
    return file_path

def log_result(file_path, ip_address, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- Scan at {timestamp} ---\n")
        if "error" in result:
            f.write(f"Error: {result['error']}\n")
        else:
            f.write(f"IP: {result['data']['ipAddress']}\n")
            f.write(f"Reputation score: {result['data']['abuseConfidenceScore']}/100\n")
            f.write(f"Country: {result['data']['countryCode']}\n")
            f.write(f"ISP: {result['data']['isp']}\n")
            f.write(f"Domain: {result['data']['domain']}\n")
            f.write(f"Is whitelisted: {'Yes' if result['data']['isWhitelisted'] else 'No'}\n")
            f.write(f"Last reported: {result['data']['lastReportedAt']}\n")
            f.write(f"Status: {'[WARNING] Likely malicious' if result['data']['abuseConfidenceScore'] > 50 else '[OK] Clean'}\n")

def run_scan(file_path):
    api_key = read_api_key()
    if not api_key:
        print("Error: Could not read API key. Please ensure 'IP_scan_api_key.txt' exists and contains a valid key.")
        return

    try:
        ip_address = requests.get("https://api.ipify.org").text
        print(f"Public IP address detected: {ip_address}")
    except Exception as e:
        print(f"Unable to detect your public IP: {e}")
        return

    result = check_ip_reputation(ip_address, api_key)
    log_result(file_path, ip_address, result)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\nScan result:")
        print(f"IP: {result['data']['ipAddress']}")
        print(f"Reputation score: {result['data']['abuseConfidenceScore']}/100")
        print(f"Country: {result['data']['countryCode']}")
        print(f"ISP: {result['data']['isp']}")
        print(f"Domain: {result['data']['domain']}")
        print(f"Is whitelisted: {'Yes' if result['data']['isWhitelisted'] else 'No'}")
        print(f"Last reported: {result['data']['lastReportedAt']}")

        if result['data']['abuseConfidenceScore'] > 50:
            print("\n⚠️ Warning: This IP has a high reputation score (likely malicious).")
        else:
            print("\n✅ This IP appears clean.")

    print(f"\nResults saved to: {file_path}")

def main():
    file_path = "IP_scan.log"

    # Check if the file exists, otherwise ask the user to create it
    if not os.path.exists(file_path):
        print("The file IP_scan.log does not exist. Creating the file...")
        if not is_tkinter_installed():
            print("tkinter is not installed. Attempting to install...")
            if not install_tkinter():
                print("Unable to install tkinter. The file will be created in the current directory as 'IP_scan.log'.")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("--- IP scan log file ---\n")
            else:
                print("tkinter installed successfully.")
                selected_path = select_save_location()
                if selected_path:
                    file_path = selected_path
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("--- IP scan log file ---\n")
                else:
                    print("No location selected. The file will be created in the current directory as 'IP_scan.log'.")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("--- IP scan log file ---\n")
    else:
        print(f"The file {file_path} already exists.")

    # Run once immediately
    print("\n--- Immediate execution ---")
    run_scan(file_path)

    # Schedule a daily execution at 1:00 AM
    schedule.every().day.at("01:00").do(run_scan, file_path=file_path)
    print("\nScript scheduled to run once a day at 1:00 AM. Press Ctrl+C to stop.")

    # Loop to run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

