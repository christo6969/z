# ClasseViva Monitor Bot for Raspberry Pi

A Telegram bot for monitoring ClasseViva (Italian school e-register) notifications, optimized for Raspberry Pi.

## Two Modes Available

### 1. Interactive Bot Mode (bot.py)
Traditional Telegram bot with commands like /start, /login, /check. Requires manual interaction.

### 2. Continuous Monitor Mode (monitor.py) ⭐ **NEW**
Fully automated continuous monitoring that runs in the background and automatically sends new communications every 60 seconds. **Recommended for Raspberry Pi 24/7 monitoring.**

See [MONITOR.md](MONITOR.md) for detailed documentation on continuous monitoring mode.

## Quick Start

### For Continuous Monitoring (Recommended)

1. **Clone and install:**
   ```bash
   git clone https://github.com/christo6969/z.git classeviva-monitor
   cd classeviva-monitor
   chmod +x install.sh
   ./install.sh
   ```

2. **Run the continuous monitor:**
   ```bash
   source venv/bin/activate
   python3 monitor.py
   ```

That's it! The monitor will run continuously, checking every 60 seconds and sending new communications automatically to Telegram.

### For Interactive Bot Mode

1. **Clone the repository:**
   ```bash
   git clone https://github.com/christo6969/z.git classeviva-monitor
   cd classeviva-monitor
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Configure credentials:**
   ```bash
   nano .env
   # Add your BOT_TOKEN, CLASSEVIVA_USERNAME, and CLASSEVIVA_PASSWORD
   ```

4. **Run the interactive bot:**
   ```bash
   source venv/bin/activate
   python bot.py
   ```

See detailed instructions below for systemd service setup.

---

## Comparison: Monitor vs Bot

| Feature | monitor.py (Continuous) | bot.py (Interactive) |
|---------|------------------------|----------------------|
| **Mode** | Fully automated | Manual commands |
| **Setup** | Zero configuration | Requires .env setup |
| **Monitoring** | Every 60 seconds | On-demand with /check |
| **Best For** | 24/7 Raspberry Pi | Interactive usage |
| **Credentials** | Hardcoded | From .env file |
| **Commands** | None (automatic) | /start, /login, /check, etc. |

---

## Features

✅ **Real-time Monitoring** - Monitor ClasseViva communications and notifications  
✅ **Intelligent Class Detection** - Automatically detects class mentions (e.g., 1AA, 2BC, 5XY)  
✅ **PDF Parsing** - Extracts and analyzes PDF attachments  
✅ **Raspberry Pi Optimized** - Memory-efficient and resource-conscious  
✅ **Auto-start** - Systemd service for automatic startup  
✅ **Kurigram Integration** - Uses custom Pyrogram fork for better performance  

## Requirements

### Hardware
- Raspberry Pi 3/4/5 or Raspberry Pi Zero 2 W
- Minimum 512MB RAM (1GB recommended)
- Internet connection

### Software
- Raspberry Pi OS (Bullseye or newer)
- Python 3.7 or higher
- Git

## Installation

### 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Dependencies

```bash
# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv git

# Install system dependencies for PDF processing
sudo apt install -y libpoppler-cpp-dev poppler-utils
```

### 3. Clone Repository

```bash
cd ~
git clone https://github.com/christo6969/z.git classeviva-monitor
cd classeviva-monitor
```

### 4. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Python Requirements

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Note:** The installation of `kurigram` (custom Pyrogram fork) might take several minutes on Raspberry Pi.

## Configuration

### 1. Create Environment File

```bash
cp .env.example .env
nano .env
```

### 2. Configure Credentials

Edit the `.env` file with your credentials:

```bash
# Telegram Bot Token (get from @BotFather on Telegram)
BOT_TOKEN=your_bot_token_here

# ClasseViva Credentials
CLASSEVIVA_USERNAME=your_username
CLASSEVIVA_PASSWORD=your_password

# API credentials (already configured, usually no need to change)
# API_ID=26534737
# API_HASH=b68693742cb2f9e6b3cb99d09bdce12f
```

### 3. Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token and paste it in the `.env` file

## Usage

### Running Continuous Monitor (monitor.py)

**Manual Run:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the continuous monitor
python3 monitor.py

# Press Ctrl+C to stop
```

**As System Service:**
```bash
# Edit service file to use monitor.py
sudo nano /etc/systemd/system/classeviva-monitor.service

# Change ExecStart line to:
# ExecStart=/path/to/venv/bin/python /path/to/monitor.py

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable classeviva-monitor
sudo systemctl start classeviva-monitor

# Check status and logs
sudo systemctl status classeviva-monitor
sudo journalctl -u classeviva-monitor -f
```

See [MONITOR.md](MONITOR.md) for detailed documentation.

### Running Interactive Bot (bot.py)

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python bot.py
```

### Running as System Service (Recommended)

This enables auto-start on boot and automatic restart on failure.

#### 1. Install Service

```bash
# Copy service file
sudo cp classeviva-monitor.service /etc/systemd/system/

# Adjust paths if needed
sudo nano /etc/systemd/system/classeviva-monitor.service

# Reload systemd
sudo systemctl daemon-reload
```

#### 2. Enable and Start Service

```bash
# Enable auto-start on boot
sudo systemctl enable classeviva-monitor

# Start the service
sudo systemctl start classeviva-monitor
```

#### 3. Check Service Status

```bash
# View status
sudo systemctl status classeviva-monitor

# View logs
sudo journalctl -u classeviva-monitor -f
```

### Bot Commands

Once the bot is running, use these commands in Telegram:

- `/start` - Welcome message and overview
- `/help` - Show help and available commands
- `/login` - Authenticate with ClasseViva
- `/check` - Manually check for new communications
- `/status` - Check connection status
- `/logout` - Disconnect from ClasseViva

### Class Detection

The bot automatically detects class mentions in the format `[1-5][A-Z]{2}`:
- Valid examples: `1AA`, `2BC`, `3XY`, `5ZZ`
- Detects classes in both text messages and PDF documents
- Shows unique classes in a separate line

**Example output:**
```
📌 Important Notice
📅 Date: 2025-01-15

The class 3AB will have the exam...
Students from 2CD should attend...

📚 Classi rilevate: 2CD, 3AB
```

## Troubleshooting

### Bot Won't Start

**Check logs:**
```bash
# If running manually
cat classeviva_monitor.log

# If running as service
sudo journalctl -u classeviva-monitor -n 50
```

**Common issues:**
1. **Missing BOT_TOKEN**: Make sure you've configured `.env` file
2. **Permission issues**: Check file permissions
3. **Port already in use**: Stop any other instances

### Memory Issues on Raspberry Pi

If you experience memory issues:

1. **Reduce concurrent workers** in `config.py`:
   ```python
   MAX_WORKERS = 1  # Reduce from 2 to 1
   ```

2. **Limit PDF size** in `config.py`:
   ```python
   MAX_PDF_SIZE_MB = 3  # Reduce from 5 to 3
   ```

3. **Add swap space:**
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Set CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

### ClasseViva Authentication Fails

1. **Check credentials** in `.env` file
2. **Verify network connection**
3. **Check ClasseViva service status** (might be down)

### PDF Processing Issues

If PDF parsing fails:

```bash
# Reinstall dependencies
sudo apt install --reinstall libpoppler-cpp-dev poppler-utils
pip install --force-reinstall PyPDF2
```

### Stop the Bot

```bash
# If running manually
Ctrl+C

# If running as service
sudo systemctl stop classeviva-monitor
```

## Performance Optimization

### For Raspberry Pi Zero/Older Models

1. **Disable logging to file** in `config.py`:
   ```python
   ENABLE_LOGGING = False
   ```

2. **Run with limited resources:**
   ```bash
   # Set CPU and memory limits
   sudo systemctl edit classeviva-monitor
   ```
   Add:
   ```
   [Service]
   MemoryLimit=128M
   CPUQuota=30%
   ```

3. **Close unnecessary programs** to free up memory

### For Raspberry Pi 4/5

The default settings should work well. You can increase workers for better performance:

```python
MAX_WORKERS = 4  # in config.py
```

## Development

### Project Structure

```
classeviva-monitor/
├── bot.py                      # Main bot application
├── config.py                   # Configuration settings
├── classeviva_api.py          # ClasseViva API integration
├── class_detector.py          # Class detection module
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── classeviva-monitor.service # Systemd service file
└── README.md                 # This file
```

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Test class detection
python -c "from class_detector import detect_classes; print(detect_classes(text='Class 1AA and 2BC'))"
```

### Updating

```bash
cd ~/classeviva-monitor
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart classeviva-monitor
```

## Technical Details

- **Framework**: Kurigram (Pyrogram fork from kurimuzonakuma/pyrogram)
- **API ID**: 26534737
- **PDF Library**: PyPDF2 (lightweight, Raspberry Pi friendly)
- **Pattern Detection**: Regex `[1-5][A-Z]{2}`
- **Resource Limits**: Configurable memory and CPU limits

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit** `.env` file to Git (it's in `.gitignore`)
2. **Protect your credentials** - don't share them
3. **Use strong passwords** for ClasseViva account
4. **Regularly update** the system and dependencies
5. **Monitor logs** for suspicious activity

## License

This project is for educational purposes. Respect ClasseViva's terms of service.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error messages

## Credits

- Uses Kurigram from [kurimuzonakuma/pyrogram](https://github.com/kurimuzonakuma/pyrogram)
- Inspired by various ClasseViva Telegram bots
- Optimized for Raspberry Pi single-board computers

---

Made with ❤️ for Raspberry Pi enthusiasts and Italian students