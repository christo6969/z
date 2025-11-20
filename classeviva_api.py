"""
ClasseViva API Integration Module
Handles authentication and communication monitoring
Based on exact authentication logic from local_monitor.py
"""

import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime
import pytz
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

logger = logging.getLogger(__name__)

# Italian timezone
ITALIAN_TZ = pytz.timezone('Europe/Rome')


def log_colored(message: str, color: str = Fore.WHITE):
    """Log with color and Italian timezone timestamp"""
    now = datetime.now(ITALIAN_TZ)
    timestamp = now.strftime('[%Y-%m-%d %H:%M:%S]')
    print(f"{timestamp} {color}{message}{Style.RESET_ALL}")


class ClasseVivaAPI:
    """ClasseViva API client for monitoring notifications and communications"""
    
    def __init__(self):
        """Initialize with hardcoded credentials"""
        # Hardcoded credentials as per requirements
        self.username = "diliochr.s@iisvoltapescara.edu.it"
        self.password = "Kei2009Kei@"
        
        self.session = requests.Session()
        self.cookies = {}
        self.phpsessid = None
        self.webidentity = None
        
        log_colored("INFO: ClasseViva API inizializzato", Fore.CYAN)
    
    def login(self) -> bool:
        """
        Authenticate with ClasseViva API using EXACT authentication code
        from local_monitor.py lines 296-358
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            log_colored("LOGIN: Tentativo di login...", Fore.CYAN)
            
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
            
            response = self.session.post(url, data=payload, headers=headers)
            response.raise_for_status()
            
            # Extract cookies (PHPSESSID and webidentity)
            if 'Set-Cookie' in response.headers or self.session.cookies:
                for cookie in self.session.cookies:
                    if cookie.name == 'PHPSESSID':
                        self.phpsessid = cookie.value
                    elif cookie.name == 'webidentity':
                        self.webidentity = cookie.value
                
                self.cookies = {
                    'PHPSESSID': self.phpsessid,
                    'webidentity': self.webidentity
                }
            
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
    
    def get_communications(self, read_status: Optional[str] = None) -> List[Dict]:
        """
        Retrieve communications from ClasseViva using EXACT API call logic
        from local_monitor.py lines 360-401
        
        Args:
            read_status: Filter by read status (not used in exact implementation)
            
        Returns:
            List of communication objects
        """
        if not self.phpsessid or not self.webidentity:
            log_colored("ERRORE: Non autenticato. Eseguire login() prima.", Fore.RED)
            return []
        
        try:
            log_colored("API: Recupero comunicazioni...", Fore.CYAN)
            
            # EXACT API URL from problem statement
            url = "https://web.spaggiari.eu/sif/app/default/bacheca_personale.php"
            
            # EXACT headers from local_monitor.py lines 278-286
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
            
            # EXACT payload from problem statement
            payload = {
                'action': 'get_comunicazioni',
                'cerca': '',
                'ncna': '1',
                'tipo_com': ''
            }
            
            # EXACT cookie handling from local_monitor.py lines 372-380
            cookies = {
                'PHPSESSID': self.phpsessid,
                'webidentity': self.webidentity
            }
            
            response = self.session.post(url, data=payload, headers=headers, cookies=cookies)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract communications
            communications = []
            if isinstance(data, dict):
                # The response structure may vary, adapt as needed
                if 'data' in data:
                    communications = data['data']
                elif 'comunicazioni' in data:
                    communications = data['comunicazioni']
                else:
                    # Try to use the data directly if it's a list
                    if isinstance(data, list):
                        communications = data
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
    
    def get_noticeboard(self) -> List[Dict]:
        """
        Retrieve noticeboard items
        
        Returns:
            List of noticeboard items
        """
        # This uses the same get_communications method
        return self.get_communications()
    
    def download_attachment(self, attachment_id: str) -> Optional[bytes]:
        """
        Download attachment (e.g., PDF file)
        
        Args:
            attachment_id: ID of the attachment to download
            
        Returns:
            Attachment content as bytes, or None if failed
        """
        if not self.phpsessid or not self.webidentity:
            log_colored("ERRORE: Non autenticato.", Fore.RED)
            return None
        
        try:
            log_colored(f"INFO: Download allegato {attachment_id}...", Fore.CYAN)
            
            # Construct download URL (may need adjustment)
            url = f"https://web.spaggiari.eu/sif/app/default/bacheca_personale.php?action=download&id={attachment_id}"
            
            cookies = {
                'PHPSESSID': self.phpsessid,
                'webidentity': self.webidentity
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.session.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            
            log_colored(f"INFO: Allegato {attachment_id} scaricato", Fore.GREEN)
            return response.content
            
        except Exception as e:
            log_colored(f"ERRORE: Download allegato fallito - {str(e)}", Fore.RED)
            return None
    
    def mark_as_read(self, event_code: str) -> bool:
        """
        Mark a communication as read
        
        Args:
            event_code: Event code to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        if not self.phpsessid or not self.webidentity:
            log_colored("ERRORE: Non autenticato.", Fore.RED)
            return False
        
        try:
            log_colored(f"INFO: Segna come letta: {event_code}...", Fore.CYAN)
            
            # This may need adjustment based on actual API
            url = "https://web.spaggiari.eu/sif/app/default/bacheca_personale.php"
            
            payload = {
                'action': 'set_letta',
                'id': event_code
            }
            
            cookies = {
                'PHPSESSID': self.phpsessid,
                'webidentity': self.webidentity
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            response = self.session.post(url, data=payload, headers=headers, cookies=cookies)
            response.raise_for_status()
            
            log_colored(f"INFO: Comunicazione {event_code} segnata come letta", Fore.GREEN)
            return True
            
        except Exception as e:
            log_colored(f"ERRORE: Segna come letta fallito - {str(e)}", Fore.RED)
            return False
