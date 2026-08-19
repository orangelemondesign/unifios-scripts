# README.md

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
