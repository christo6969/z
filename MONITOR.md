# ClasseViva Continuous Monitor

## Overview

The `monitor.py` script is a continuous monitoring bot that runs on Raspberry Pi and checks ClasseViva for new communications every 60 seconds. When new communications are found, they are sent via Telegram along with detected classes and file attachments.

## Features

✅ **Continuous Monitoring**: Checks for new communications every 60 seconds  
✅ **EXACT Authentication**: Uses the exact authentication logic from the reference implementation  
✅ **Hardcoded Credentials**: No configuration needed - credentials are built-in  
✅ **Smart First Run**: On first run, fetches all communications but sends only the latest one  
✅ **Class Detection**: Automatically detects class mentions (1AA, 2BC, etc.) in text and PDFs  
✅ **File Attachments**: Downloads and sends PDF attachments via Telegram  
✅ **State Management**: Tracks sent communications to avoid duplicates  
✅ **Session Management**: Re-authenticates before each check to handle session expiration  
✅ **Colored Logging**: Beautiful console output with Italian timezone  
✅ **Graceful Shutdown**: Handles Ctrl+C cleanly  

## How It Works

### First Run Behavior

When you run the monitor for the first time (or when `state.json` doesn't exist):

1. **Login**: Authenticates with ClasseViva
2. **Fetch All**: Retrieves ALL communications using `ncna=0`
3. **Send Latest**: Sends ONLY the latest (first) communication to Telegram
4. **Save All Hashes**: Saves hashes of ALL communications to `state.json`
5. **Start Monitoring**: Begins the continuous monitoring loop

This ensures you don't get spammed with old communications on first run.

### Continuous Monitoring

After the first run, every 60 seconds:

1. **Login**: Creates a new session and authenticates
2. **Fetch New**: Retrieves only NEW communications using `ncna=1`
3. **Check State**: Compares against saved hashes in `state.json`
4. **Process New**: For each new communication:
   - Detects classes in text
   - Downloads PDF attachments (if any)
   - Detects classes in PDFs
   - Sends message to Telegram with detected classes
   - Sends attachments (single file or media group)
   - Updates state
5. **Save State**: Updates `state.json` with new hashes
6. **Wait**: Sleeps for 60 seconds and repeats

## Usage

### Running Manually

```bash
cd /home/runner/work/z/z
python3 monitor.py
```

### Running as a Service

For automatic startup on Raspberry Pi, you can create a systemd service:

```bash
# Edit the service file to point to monitor.py instead of bot.py
sudo nano /etc/systemd/system/classeviva-monitor.service

# Update the ExecStart line:
# ExecStart=/home/pi/classeviva-monitor/venv/bin/python /home/pi/classeviva-monitor/monitor.py

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart classeviva-monitor
```

### Stopping the Monitor

- **Manual Run**: Press `Ctrl+C`
- **Service**: `sudo systemctl stop classeviva-monitor`

## Configuration

All configuration is hardcoded in the script:

```python
CLASSEVIVA_USERNAME = "diliochr.s@iisvoltapescara.edu.it"
CLASSEVIVA_PASSWORD = "Kei2009Kei@"
TELEGRAM_BOT_TOKEN = "8555475398:AAHXA7ibbXLUNqUi_JMdybdnWcWx1j8n_3I"
TELEGRAM_CHAT_ID = "106338249"
CHECK_INTERVAL = 60  # seconds
```

To change these values, edit `monitor.py` directly.

## State File

The monitor uses `state.json` to track which communications have been sent. This file contains:

```json
{
  "sent_hashes": [
    "abc123...",
    "def456...",
    ...
  ]
}
```

**Important**: 
- Delete `state.json` to reset and re-send the latest communication
- The file is automatically created on first run
- It's excluded from git via `.gitignore`

## Logging

The monitor uses colored logging with Italian timezone:

- **GREEN**: Successful operations (login, API calls, Telegram sends)
- **RED**: Errors (login failures, API errors)
- **YELLOW**: Warnings and important notices
- **CYAN**: Info messages (status updates)

Example log output:

```
[2025-01-15 10:00:00] LOGIN: Tentativo di login...
[2025-01-15 10:00:01] LOGIN: Login riuscito!
[2025-01-15 10:00:01] API: Recupero comunicazioni...
[2025-01-15 10:00:02] API: Recuperate 5 comunicazioni
[2025-01-15 10:00:02] INFO: 2 NUOVE COMUNICAZIONI!
[2025-01-15 10:00:02] ALLEGATI: Trovati 1 allegati
[2025-01-15 10:00:03] DOWNLOAD: Scaricato documento.pdf
[2025-01-15 10:00:04] TELEGRAM: Messaggio inviato
[2025-01-15 10:00:05] STATE: Salvate 7 comunicazioni
```

## Class Detection

The monitor automatically detects class mentions in:

1. **Communication Title**: The `evtText` or `titolo` field
2. **Communication Body**: The `notes` or `testo` field
3. **PDF Attachments**: Text extracted from downloaded PDFs

Detected classes are shown in the Telegram message:

```
📌 Important Notice
📅 Data: 2025-01-15 10:00:00

Students from class 1AA and 2BC should attend...

📚 Classi rilevate: 1AA, 2BC
```

## File Attachments

### Single Attachment

When a communication has one PDF attachment:
- The file is downloaded to `/tmp/`
- Sent via `sendDocument` with the message as caption
- The temporary file is deleted after sending

### Multiple Attachments

When a communication has multiple attachments:
- All files are downloaded to `/tmp/`
- The message is sent first
- Files are sent as a media group via `sendMediaGroup`
- All temporary files are deleted after sending

## API Details

### Authentication

Uses the **EXACT** authentication logic from `local_monitor.py`:

```python
URL: https://web.spaggiari.eu/auth-p7/app/default/AuthApi4.php?a=aLoginPwd
Method: POST
Payload: {
    'uid': username,
    'pwd': password,
    'cid': '',
    'pin': '',
    'target': ''
}
```

Extracts `PHPSESSID` and `webidentity` cookies for subsequent requests.

### Get Communications

```python
URL: https://web.spaggiari.eu/sif/app/default/bacheca_personale.php
Method: POST
Payload: {
    'action': 'get_comunicazioni',
    'cerca': '',
    'ncna': '0' or '1',  # 0 = all, 1 = new only
    'tipo_com': ''
}
```

### Download Attachment

```python
URL: https://web.spaggiari.eu/sif/app/default/bacheca_personale.php?action=download&id={attachment_id}
Method: GET
```

## Telegram Integration

Uses the Telegram Bot API directly (not pyrogram) for sending messages:

- **sendMessage**: For text messages
- **sendDocument**: For single file attachments
- **sendMediaGroup**: For multiple file attachments

Messages use HTML formatting with emoji for better readability.

## Error Handling

The monitor is designed to be resilient:

- **Login Failures**: Logged as errors, next check will try again
- **API Errors**: Logged as errors, monitoring continues
- **Telegram Errors**: Logged as errors, monitoring continues
- **Download Errors**: Logged as warnings, message is still sent
- **PDF Parsing Errors**: Logged as warnings, class detection from text still works

Even if errors occur, the monitor will continue running and retry on the next cycle.

## Testing

Run the test suite to verify components:

```bash
python3 test_monitor.py
```

This tests:
- Colored logging
- Italian timezone
- State management
- Telegram notifier
- ClasseViva monitor
- Attachment parsing

## Troubleshooting

### Monitor Doesn't Start

Check Python version and dependencies:

```bash
python3 --version  # Should be 3.7+
pip3 install -r requirements.txt
```

### No Messages Received

Check Telegram credentials:

```bash
# Test bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Test sending message
curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage \
  -d chat_id=<YOUR_CHAT_ID> \
  -d text="Test"
```

### State File Issues

Reset the state:

```bash
rm state.json
# Next run will be treated as first run
```

### Memory Issues on Raspberry Pi

The monitor is lightweight, but if you experience issues:

- Reduce check interval to 120 seconds (edit `CHECK_INTERVAL`)
- Limit concurrent operations
- Monitor with `htop` or `free -h`

## Differences from bot.py

| Feature | bot.py | monitor.py |
|---------|--------|------------|
| Mode | Interactive Telegram bot | Continuous background monitor |
| Commands | /start, /login, /check, etc. | No commands - fully automated |
| Monitoring | On-demand (manual /check) | Every 60 seconds automatically |
| Authentication | Manual /login command | Automatic before each check |
| Credentials | From .env file | Hardcoded in script |
| Framework | Pyrogram (kurigram) | Direct Telegram API + requests |

## Security Note

⚠️ **WARNING**: This script contains hardcoded credentials. Do not share it publicly or commit it to a public repository. For production use, consider:

- Using environment variables
- Encrypting credentials
- Restricting file permissions: `chmod 600 monitor.py`

## Dependencies

Required Python packages:

- `requests` - HTTP requests to ClasseViva API
- `beautifulsoup4` - HTML parsing for attachments
- `colorama` - Colored console output
- `pytz` - Timezone support (Europe/Rome)
- `PyPDF2` - PDF text extraction for class detection

All dependencies are in `requirements.txt`.

## Support

For issues or questions:

1. Check the logs for error messages
2. Verify credentials are correct
3. Test network connectivity
4. Run the test suite: `python3 test_monitor.py`
5. Check ClasseViva service status

---

**Created for Raspberry Pi continuous monitoring of ClasseViva communications with automatic Telegram notifications.**
