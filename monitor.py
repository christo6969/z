#!/usr/bin/env python3
"""
ClasseViva Continuous Monitor Bot
Runs continuously on Raspberry Pi, monitoring ClasseViva communications every 60 seconds

Based on EXACT authentication and API logic from christo6969/classeviva-monitor/local_monitor.py
With hardcoded credentials and class detection integration
"""

import os
import sys
import json
import time
import hashlib
import requests
import signal
from datetime import datetime
from typing import Optional, Dict, List, Set
from bs4 import BeautifulSoup
import pytz
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Import class detector
from class_detector import detect_classes

# Italian timezone
ITALIAN_TZ = pytz.timezone('Europe/Rome')

# Hardcoded credentials as per requirements
CLASSEVIVA_USERNAME = "diliochr.s@iisvoltapescara.edu.it"
CLASSEVIVA_PASSWORD = "Kei2009Kei@"
TELEGRAM_BOT_TOKEN = "8555475398:AAHXA7ibbXLUNqUi_JMdybdnWcWx1j8n_3I"
TELEGRAM_CHAT_ID = "106338249"

# State file
STATE_FILE = "state.json"

# Monitoring interval (seconds)
CHECK_INTERVAL = 60


def log_colored(message: str, color: str = Fore.WHITE):
    """Log with color and Italian timezone timestamp"""
    now = datetime.now(ITALIAN_TZ)
    timestamp = now.strftime('[%Y-%m-%d %H:%M:%S]')
    print(f"{timestamp} {color}{message}{Style.RESET_ALL}")


class TelegramNotifier:
    """
    Telegram notification sender
    Based on EXACT TelegramNotifier class from local_monitor.py lines 39-260
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str) -> bool:
        """Send a text message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            log_colored("TELEGRAM: Messaggio inviato", Fore.GREEN)
            return True
        except Exception as e:
            log_colored(f"ERRORE: Invio messaggio Telegram fallito - {str(e)}", Fore.RED)
            return False
    
    def send_document(self, document_path: str, caption: str = "") -> bool:
        """Send a document to Telegram"""
        try:
            url = f"{self.base_url}/sendDocument"
            with open(document_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
            log_colored(f"TELEGRAM: Documento inviato ({os.path.basename(document_path)})", Fore.GREEN)
            return True
        except Exception as e:
            log_colored(f"ERRORE: Invio documento Telegram fallito - {str(e)}", Fore.RED)
            return False
    
    def send_media_group(self, media_paths: List[str], caption: str = "") -> bool:
        """Send multiple documents as a media group"""
        try:
            url = f"{self.base_url}/sendMediaGroup"
            media = []
            files = {}
            
            for i, path in enumerate(media_paths):
                attach_name = f"attach_{i}"
                media.append({
                    'type': 'document',
                    'media': f"attach://{attach_name}",
                    'caption': caption if i == 0 else ""
                })
                files[attach_name] = open(path, 'rb')
            
            data = {
                'chat_id': self.chat_id,
                'media': json.dumps(media)
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
            
            # Close all file handles
            for f in files.values():
                f.close()
            
            response.raise_for_status()
            log_colored(f"TELEGRAM: Media group inviato ({len(media_paths)} file)", Fore.GREEN)
            return True
        except Exception as e:
            log_colored(f"ERRORE: Invio media group Telegram fallito - {str(e)}", Fore.RED)
            return False
    
    def format_communication(self, comm: Dict, classes: Set[str] = None) -> str:
        """
        Format communication for Telegram with class detection
        Based on format_communication from local_monitor.py
        """
        title = comm.get("evtText", comm.get("titolo", "Nessun titolo"))
        date = comm.get("evtDatetimeBegin", comm.get("data", "Data sconosciuta"))
        notes = comm.get("notes", comm.get("testo", ""))
        
        # Build message
        message = f"<b>📌 {title}</b>\n"
        message += f"📅 Data: {date}\n"
        
        if notes:
            message += f"\n{notes}\n"
        
        # Add detected classes
        if classes:
            sorted_classes = sorted(classes)
            message += f"\n📚 Classi rilevate: {', '.join(sorted_classes)}\n"
        
        return message


class ClasseVivaMonitor:
    """
    ClasseViva Monitor class
    Based on EXACT ClasseVivaMonitor class from local_monitor.py lines 262-483
    Uses EXACT login() and get_communications() methods
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = None
        self.phpsessid = None
        self.webidentity = None
    
    def login(self) -> bool:
        """
        EXACT login method from local_monitor.py lines 296-358
        Authenticate with ClasseViva API
        """
        try:
            log_colored("LOGIN: Tentativo di login...", Fore.CYAN)
            
            # Create new session for each login
            self.session = requests.Session()
            
            # EXACT login URL from local_monitor.py
            url = "https://web.spaggiari.eu/auth-p7/app/default/AuthApi4.php?a=aLoginPwd"
            
            # EXACT headers from local_monitor.py lines 301-316
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://web.spaggiari.eu',
                'Referer': 'https://web.spaggiari.eu/auth-p7/app/default/login.php',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # EXACT payload format from local_monitor.py line 318
            payload = {
                'uid': self.username,
                'pwd': self.password,
                'cid': '',
                'pin': '',
                'target': ''
            }
            
            response = self.session.post(url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Extract cookies (PHPSESSID and webidentity) - EXACT logic from local_monitor.py
            if 'Set-Cookie' in response.headers or self.session.cookies:
                for cookie in self.session.cookies:
                    if cookie.name == 'PHPSESSID':
                        self.phpsessid = cookie.value
                    elif cookie.name == 'webidentity':
                        self.webidentity = cookie.value
            
            # Check response
            data = response.json()
            
            if data and not data.get('error'):
                log_colored("LOGIN: Login riuscito!", Fore.GREEN)
                return True
            else:
                log_colored(f"ERRORE: Login fallito - {data.get('error', 'Unknown error')}", Fore.RED)
                return False
                
        except Exception as e:
            log_colored(f"ERRORE: Login fallito - {str(e)}", Fore.RED)
            return False
    
    def get_communications(self, ncna: int = 1) -> List[Dict]:
        """
        EXACT get_communications method from local_monitor.py lines 360-401
        Retrieve communications from ClasseViva
        
        Args:
            ncna: 0 = get all, 1 = get only new
        """
        if not self.phpsessid or not self.webidentity:
            log_colored("ERRORE: Non autenticato. Eseguire login() prima.", Fore.RED)
            return []
        
        try:
            log_colored("API: Recupero comunicazioni...", Fore.CYAN)
            
            # EXACT API URL
            url = "https://web.spaggiari.eu/sif/app/default/bacheca_personale.php"
            
            # EXACT headers from local_monitor.py
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://web.spaggiari.eu',
                'Referer': 'https://web.spaggiari.eu/sif/app/default/bacheca_personale.php'
            }
            
            # EXACT payload - ncna parameter controls new vs all
            payload = {
                'action': 'get_comunicazioni',
                'cerca': '',
                'ncna': str(ncna),
                'tipo_com': ''
            }
            
            # EXACT cookie handling
            cookies = {
                'PHPSESSID': self.phpsessid,
                'webidentity': self.webidentity
            }
            
            response = self.session.post(url, data=payload, headers=headers, cookies=cookies, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract communications from response
            communications = []
            if isinstance(data, dict):
                if 'data' in data:
                    communications = data['data']
                elif 'comunicazioni' in data:
                    communications = data['comunicazioni']
            elif isinstance(data, list):
                communications = data
            
            log_colored(f"API: Recuperate {len(communications)} comunicazioni", Fore.GREEN)
            
            # Count new communications
            new_count = len([c for c in communications if not c.get('letta', True)])
            if new_count > 0:
                log_colored(f"INFO: {new_count} NUOVE COMUNICAZIONI!", Fore.YELLOW)
            
            return communications
            
        except Exception as e:
            log_colored(f"ERRORE: Recupero comunicazioni fallito - {str(e)}", Fore.RED)
            return []
    
    def download_attachment(self, attachment_id: str, filename: str) -> Optional[str]:
        """
        Download attachment and save to file
        Returns path to downloaded file or None if failed
        """
        if not self.phpsessid or not self.webidentity:
            log_colored("ERRORE: Non autenticato.", Fore.RED)
            return None
        
        try:
            log_colored(f"DOWNLOAD: Scaricamento {filename}...", Fore.CYAN)
            
            # Construct download URL
            url = f"https://web.spaggiari.eu/sif/app/default/bacheca_personale.php?action=download&id={attachment_id}"
            
            cookies = {
                'PHPSESSID': self.phpsessid,
                'webidentity': self.webidentity
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.session.get(url, headers=headers, cookies=cookies, timeout=60)
            response.raise_for_status()
            
            # Save to file
            filepath = f"/tmp/{filename}"
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            log_colored(f"DOWNLOAD: Scaricato {filename}", Fore.GREEN)
            return filepath
            
        except Exception as e:
            log_colored(f"ERRORE: Download allegato fallito - {str(e)}", Fore.RED)
            return None
    
    def parse_attachments(self, comm: Dict) -> List[Dict]:
        """
        Parse HTML to find attachment IDs
        Returns list of attachment info dicts
        """
        attachments = []
        
        # Check for attachments in the communication
        if 'allegati' in comm and comm['allegati']:
            # Direct allegati field
            for allegato in comm['allegati']:
                attachments.append({
                    'id': allegato.get('allegato_id', ''),
                    'filename': allegato.get('filename', f"allegato_{allegato.get('allegato_id', 'unknown')}.pdf")
                })
        elif 'notes' in comm or 'testo' in comm:
            # Parse HTML notes for attachment links
            notes_html = comm.get('notes', comm.get('testo', ''))
            if notes_html and 'allegato' in notes_html.lower():
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(notes_html, 'html.parser')
                    
                    # Find attachment links
                    for link in soup.find_all('a'):
                        href = link.get('href', '')
                        if 'allegato_id' in href or 'download' in href:
                            # Extract allegato_id from href
                            import re
                            match = re.search(r'allegato_id=(\d+)', href)
                            if match:
                                allegato_id = match.group(1)
                                filename = link.get_text(strip=True) or f"allegato_{allegato_id}.pdf"
                                if not filename.endswith('.pdf'):
                                    filename += '.pdf'
                                attachments.append({
                                    'id': allegato_id,
                                    'filename': filename
                                })
                except Exception as e:
                    log_colored(f"ERRORE: Parsing allegati fallito - {str(e)}", Fore.YELLOW)
        
        if attachments:
            log_colored(f"ALLEGATI: Trovati {len(attachments)} allegati", Fore.CYAN)
        
        return attachments
    
    def check_updates(self, state: Dict, is_first_run: bool = False) -> int:
        """
        EXACT check_updates method from local_monitor.py lines 435-483
        Check for new communications and send to Telegram
        
        Args:
            state: Dictionary containing seen communication hashes
            is_first_run: If True, fetch all but send only latest
        
        Returns:
            Number of new communications processed
        """
        # Login before each check (to handle session expiration)
        if not self.login():
            return 0
        
        # Fetch communications
        if is_first_run:
            # First run: fetch ALL communications (ncna=0)
            communications = self.get_communications(ncna=0)
        else:
            # Continuous monitoring: fetch only new (ncna=1)
            communications = self.get_communications(ncna=1)
        
        if not communications:
            return 0
        
        # Initialize Telegram notifier
        notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Track new communications
        new_count = 0
        
        # On first run, send only the latest (first) communication
        if is_first_run:
            comms_to_send = [communications[0]] if communications else []
        else:
            # On subsequent runs, send all new communications
            comms_to_send = communications
        
        for comm in comms_to_send:
            # Generate hash for this communication
            comm_id = comm.get('evtId', comm.get('id', ''))
            comm_hash = hashlib.md5(str(comm_id).encode()).hexdigest()
            
            # Check if already sent
            if comm_hash in state.get('sent_hashes', []):
                continue
            
            # Extract text for class detection
            title = comm.get("evtText", comm.get("titolo", ""))
            notes = comm.get("notes", comm.get("testo", ""))
            comm_text = f"{title} {notes}"
            
            # Detect classes from text
            from class_detector import ClassDetector
            detector = ClassDetector()
            classes = detector.detect_classes_in_text(comm_text)
            
            # Parse attachments
            attachments = self.parse_attachments(comm)
            
            # Download PDF attachments and detect classes in them
            attachment_paths = []
            for attachment in attachments:
                filepath = self.download_attachment(attachment['id'], attachment['filename'])
                if filepath:
                    attachment_paths.append(filepath)
                    
                    # Detect classes in PDF
                    try:
                        with open(filepath, 'rb') as f:
                            pdf_content = f.read()
                        pdf_classes = detector.detect_classes_in_pdf(pdf_content)
                        classes.update(pdf_classes)
                    except Exception as e:
                        log_colored(f"ERRORE: Analisi PDF fallita - {str(e)}", Fore.YELLOW)
            
            # Format and send message
            message = notifier.format_communication(comm, classes)
            
            # Send message
            if attachment_paths:
                # Send with attachments
                if len(attachment_paths) == 1:
                    notifier.send_document(attachment_paths[0], caption=message)
                else:
                    # Send message first, then media group
                    notifier.send_message(message)
                    notifier.send_media_group(attachment_paths)
                
                # Clean up downloaded files
                for filepath in attachment_paths:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
            else:
                # Send message only
                notifier.send_message(message)
            
            # Mark as sent
            if 'sent_hashes' not in state:
                state['sent_hashes'] = []
            state['sent_hashes'].append(comm_hash)
            new_count += 1
        
        # On first run, save ALL communication hashes (not just the one we sent)
        if is_first_run:
            for comm in communications:
                comm_id = comm.get('evtId', comm.get('id', ''))
                comm_hash = hashlib.md5(str(comm_id).encode()).hexdigest()
                if comm_hash not in state.get('sent_hashes', []):
                    state['sent_hashes'].append(comm_hash)
        
        # Save state
        save_state(state)
        log_colored(f"STATE: Salvate {len(state.get('sent_hashes', []))} comunicazioni", Fore.GREEN)
        
        return new_count


def load_state() -> Dict:
    """Load state from JSON file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            log_colored(f"ERRORE: Caricamento state fallito - {str(e)}", Fore.YELLOW)
    
    return {'sent_hashes': []}


def save_state(state: Dict):
    """Save state to JSON file"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log_colored(f"ERRORE: Salvataggio state fallito - {str(e)}", Fore.RED)


def print_banner():
    """Print startup banner"""
    print()
    print("=" * 70)
    print("  ClasseViva Continuous Monitor")
    print("  Monitoring ClasseViva communications every 60 seconds")
    print("=" * 70)
    print()
    log_colored(f"Username: {CLASSEVIVA_USERNAME}", Fore.CYAN)
    log_colored(f"Chat ID: {TELEGRAM_CHAT_ID}", Fore.CYAN)
    log_colored(f"Check Interval: {CHECK_INTERVAL} seconds", Fore.CYAN)
    print()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print()
    log_colored("STOP: Interruzione ricevuta. Arresto monitor...", Fore.YELLOW)
    sys.exit(0)


def main():
    """Main execution loop"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Print banner
    print_banner()
    
    # Initialize monitor
    monitor = ClasseVivaMonitor(CLASSEVIVA_USERNAME, CLASSEVIVA_PASSWORD)
    
    # Load state
    state = load_state()
    
    # Check if this is first run
    is_first_run = len(state.get('sent_hashes', [])) == 0
    
    if is_first_run:
        log_colored("INFO: Prima esecuzione - invio ultima comunicazione", Fore.CYAN)
    else:
        log_colored("INFO: Ripresa monitoraggio", Fore.CYAN)
    
    # First check
    log_colored("INFO: Primo controllo...", Fore.CYAN)
    new_count = monitor.check_updates(state, is_first_run=is_first_run)
    log_colored(f"INFO: Primo controllo completato ({new_count} nuove)", Fore.GREEN)
    
    # Start continuous monitoring loop
    log_colored(f"INFO: Avvio monitoraggio continuo (ogni {CHECK_INTERVAL} secondi)", Fore.CYAN)
    log_colored("INFO: Premi Ctrl+C per arrestare", Fore.YELLOW)
    print()
    
    while True:
        try:
            # Wait for next check
            time.sleep(CHECK_INTERVAL)
            
            # Check for updates
            new_count = monitor.check_updates(state, is_first_run=False)
            
            if new_count > 0:
                log_colored(f"INFO: Trovate e inviate {new_count} nuove comunicazioni", Fore.GREEN)
            else:
                log_colored("INFO: Nessuna nuova comunicazione", Fore.CYAN)
        
        except Exception as e:
            log_colored(f"ERRORE: Errore nel loop principale - {str(e)}", Fore.RED)
            # Continue monitoring even if there's an error
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
