# GPU Track Slack Bot

A Python-based solution for monitoring GPU usage on servers, designed to send alerts to Slack when unauthorized usage is detected or when users violate their assigned GPU allocations.

## Features

1. **Unauthorized User Alerts**
   - Monitors GPU usage every 10 minutes.
   - Sends a Slack notification if an unregistered user is detected using the GPU.

2. **Misallocation Alerts**
   - Alerts when a user occupies a GPU not assigned to them unless explicitly noted in exceptions.

3. **Integration with Google Sheets**
   - Authorized users and exceptions are dynamically managed via a Google Sheets document.

## Requirements

- **Python 3.7 or above**
- **Google API Client Library**: `google-api-python-client`
- **Slack Workspace**: Configured with an Incoming Webhook URL

## Files

### `get_gpu_id_from_sp.py`
- Fetches authorized and exception users from Google Sheets.
- Connects to Google Sheets via a service account.

### `gpu_monitor.sh`
- A Bash script to run the Python monitoring script every 10 minutes.
- Configurable using `cron`.

### `gpu_track.py`
- The main Python script:
  - Monitors GPU usage using `nvidia-smi`.
  - Compares active GPU users with authorized and exception users.
  - Sends alerts to Slack via Incoming Webhooks.

### `google_spreadsheets_api.json`
- A service account key file required to access the Google Sheets API.
- **Ensure this file is kept secure and excluded from public repositories.**

## Installation

### 1. Clone the Repository
Run the following commands to clone the repository:
```bash
conda activate base
git clone https://github.com/JEONG-HO-JAE/gpu_track_slack_bot.git
cd gpu_track_slack_bot
```

### 2. Install required Python packages:
Install the necessary Python packages using pip:
```bash
pip install google-api-python-client
```

### 3. Set Up the Google Sheets API
- Ensure the google_spreadsheets_api.json file is properly configured.
- Share your Google Sheet with the service account email provided in google_spreadsheets_api.json.

### 4. Configure the Slack Incoming Webhook URL
Edit the gpu_track.py file to include your Slack Webhook URL:
```python
WEBHOOK_URL = "https://hooks.slack.com/services/..."
```

### 5. Make the Monitoring Script Executable
Grant execute permissions to the monitoring script:
```bash
chmod +x gpu_monitor.sh
```

### 6.	Add the Script to crontab
Open the crontab file for editing:
```bash
crontab -e
```
Add the following line to the crontab to run the script every 10 minutes:
```bash
*/10 * * * * /bin/bash /path/to/gpu_monitor.sh >> /path/to/gpu_monitor.log 2>&1
```


### 7. Usage
Run the Monitoring Script Manually | To test the script manually, run:
```bash
./gpu_monitor.sh
```
View Logs | To check the logs:
```bash
cat /path/to/gpu_monitor.log
```

### License  
This project is licensed under the MIT License.