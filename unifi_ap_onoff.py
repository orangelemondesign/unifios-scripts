import sys
import requests
import urllib3
import csv
import getpass
import os

# Suppress unverified HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=== UniFi AP Bulk Controller ===")

# --- Form Filling / Interactive Prompts ---
controller = input("Controller URL [https://10.10.10.2:11443]: ").strip() or "https://10.10.10.2:11443"
username = input("Username: ").strip()

# getpass hides the password as you type it for security
password = getpass.getpass("Password: ").strip()

site = input("Site ID [default]: ").strip() or "default"

csv_path = input("CSV Filename [mac_addresses.csv]: ").strip() or "mac_addresses.csv"

action_input = input("Action to perform (enable/disable): ").strip().lower()
if action_input not in ['enable', 'disable']:
    print("Invalid action. Please type 'enable' or 'disable'.")
    sys.exit(1)

action_state = False if action_input == 'enable' else True

# --- Read CSV File ---
if not os.path.exists(csv_path):
    print(f"Error: Could not find the file '{csv_path}'.")
    sys.exit(1)

ap_macs = []
with open(csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        if row: # Skip empty lines
            # Grab the first column, strip whitespace
            mac = row[0].strip()
            # Simple check to skip a header row if it exists
            if "mac" not in mac.lower(): 
                ap_macs.append(mac)

if not ap_macs:
    print("No valid MAC addresses found in the CSV.")
    sys.exit(1)

print(f"\nLoaded {len(ap_macs)} MAC addresses from {csv_path}. Connecting to controller...\n")

# --- Session Setup ---
s = requests.Session()
s.verify = False

# 1. Authenticate to UniFi OS
login_payload = {"username": username, "password": password}
r_login = s.post(f"{controller}/api/auth/login", json=login_payload)

if r_login.status_code != 200:
    print(f"Login failed! Status Code: {r_login.status_code}")
    sys.exit(1)

# 2. Extract CSRF Token (Required for UniFi OS)
csrf_token = r_login.headers.get('x-csrf-token')
if csrf_token:
    s.headers.update({'X-CSRF-Token': csrf_token})
else:
    print("Warning: No CSRF token found in login response.")

# 3. Get Device IDs for all MACs
r_devices = s.get(f"{controller}/proxy/network/api/s/{site}/stat/device")
devices = r_devices.json().get('data', [])

target_macs = [mac.lower() for mac in ap_macs]
devices_to_update = []

for dev in devices:
    mac = dev.get('mac', '').lower()
    if mac in target_macs:
        devices_to_update.append({
            'id': dev.get('_id'),
            'mac': mac,
            'name': dev.get('name', mac)
        })

if not devices_to_update:
    print("None of the MAC addresses in your CSV matched the APs on the controller.")
    s.post(f"{controller}/api/auth/logout")
    sys.exit(1)

# 4. Loop through and update each AP
state_text = "Disabled (OFF)" if action_state else "Enabled (ON)"

for ap in devices_to_update:
    print(f"Processing AP: {ap['name']} ({ap['mac']})...")
    update_payload = {"disabled": action_state}
    r_update = s.put(f"{controller}/proxy/network/api/s/{site}/rest/device/{ap['id']}", json=update_payload)

    if r_update.status_code == 200:
        print(f"  -> Success: {ap['name']} is now {state_text}")
    else:
        print(f"  -> Failed to update {ap['name']}. HTTP Status: {r_update.status_code}")

# 5. Logout to clear session
s.post(f"{controller}/api/auth/logout")
print("\nFinished processing.")
