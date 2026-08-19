import sys
import requests
import urllib3
import csv
import json
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Handle Command Line Argument for Cron
if len(sys.argv) < 2 or sys.argv[1].lower() not in ['enable', 'disable']:
    print("Usage: python3 unifi_cron.py [enable|disable]")
    sys.exit(1)

action_state = False if sys.argv[1].lower() == 'enable' else True

# 2. Setup Absolute Paths (Crucial for cron)
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.json')

# 3. Load Credentials Safely
if not os.path.exists(config_path):
    print(f"Error: Config file not found at {config_path}")
    sys.exit(1)

with open(config_path, 'r') as f:
    config = json.load(f)

CONTROLLER = config.get("controller", "https://10.10.10.2:11443")
USERNAME = config.get("username")
PASSWORD = config.get("password")
SITE = config.get("site", "default")
csv_filename = config.get("csv_file", "mac_addresses.csv")
csv_path = os.path.join(script_dir, csv_filename)

# 4. Load MAC Addresses from CSV
if not os.path.exists(csv_path):
    print(f"Error: CSV file not found at {csv_path}")
    sys.exit(1)

ap_macs = []
with open(csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        if row:
            mac = row[0].strip()
            if "mac" not in mac.lower(): 
                ap_macs.append(mac)

if not ap_macs:
    print("No valid MAC addresses found in the CSV.")
    sys.exit(1)

# 5. Connect and Execute Update
s = requests.Session()
s.verify = False

r_login = s.post(f"{CONTROLLER}/api/auth/login", json={"username": USERNAME, "password": PASSWORD})
if r_login.status_code != 200:
    print(f"Login failed! Status: {r_login.status_code}")
    sys.exit(1)

csrf_token = r_login.headers.get('x-csrf-token')
if csrf_token:
    s.headers.update({'X-CSRF-Token': csrf_token})

r_devices = s.get(f"{CONTROLLER}/proxy/network/api/s/{SITE}/stat/device")
devices = r_devices.json().get('data', [])

target_macs = [mac.lower() for mac in ap_macs]
devices_to_update = [{'id': dev.get('_id'), 'mac': dev.get('mac', '').lower(), 'name': dev.get('name', dev.get('mac'))} for dev in devices if dev.get('mac', '').lower() in target_macs]

state_text = "Disabled (OFF)" if action_state else "Enabled (ON)"

for ap in devices_to_update:
    r_update = s.put(f"{CONTROLLER}/proxy/network/api/s/{SITE}/rest/device/{ap['id']}", json={"disabled": action_state})
    if r_update.status_code == 200:
        print(f"Success: {ap['name']} -> {state_text}")
    else:
        print(f"Failed: {ap['name']}")

s.post(f"{CONTROLLER}/api/auth/logout")
