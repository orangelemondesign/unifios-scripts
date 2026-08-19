# README.md

## Create the Configuration File
In the same folder as your Python script and CSV file, create a file named config.json. Put your credentials and settings here:
```
{
    "controller": "https://10.10.10.2:11443",
    "username": "your_local_admin",
    "password": "your_password",
    "site": "default",
    "csv_file": "mac_addresses.csv"
}
```

To prevent other users on the server from reading your password, restrict the file permissions so only your user account can read it. Run this in your terminal:
```
chmod 600 config.json
```
## The Automated Python Script
download file unifi_ap_onoff.py


## Automatically Off and On Unifi Access Point using cron:

Open your crontab editor (crontab -e).
Because cron runs in a minimal environment, you must provide the full absolute path to both Python and your script. To find the path to python, type which python3 in your terminal.
Add these lines to set your schedule (e.g., OFF at 11 PM, ON at 6 AM):

BASH Command:
```
# Turn OFF APs from the CSV at 23:00 everyday
0 23 * * * /usr/bin/python3 /full/path/to/your/folder/unifi_cron.py disable

# Turn ON APs from the CSV at 06:00 everyday
0 6 * * * /usr/bin/python3 /full/path/to/your/folder/unifi_cron.py enable
```
