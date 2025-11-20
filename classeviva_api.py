"""
ClasseViva API Integration Module
Handles authentication and communication monitoring
"""

import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime

from config import CLASSEVIVA_API_URL

logger = logging.getLogger(__name__)


class ClasseVivaAPI:
    """ClasseViva API client for monitoring notifications and communications"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.auth_token = None
        self.base_url = CLASSEVIVA_API_URL
    
    def login(self) -> bool:
        """
        Authenticate with ClasseViva API
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "uid": self.username,
                "pass": self.password
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.auth_token = data.get("token")
            
            if self.auth_token:
                logger.info("Successfully authenticated with ClasseViva")
                return True
            else:
                logger.error("No token received from ClasseViva")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        return {
            "Z-Auth-Token": self.auth_token,
            "Content-Type": "application/json"
        }
    
    def get_communications(self, read_status: Optional[str] = None) -> List[Dict]:
        """
        Retrieve communications from ClasseViva
        
        Args:
            read_status: Filter by read status (None for all, 'read', 'unread')
            
        Returns:
            List of communication objects
        """
        if not self.auth_token:
            logger.warning("Not authenticated. Call login() first.")
            return []
        
        try:
            url = f"{self.base_url}/students/agenda/all"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            communications = data.get("agenda", [])
            
            # Filter by read status if specified
            if read_status == "unread":
                communications = [c for c in communications if not c.get("evtRead", False)]
            elif read_status == "read":
                communications = [c for c in communications if c.get("evtRead", False)]
            
            logger.info(f"Retrieved {len(communications)} communications")
            return communications
            
        except Exception as e:
            logger.error(f"Failed to get communications: {e}")
            return []
    
    def get_noticeboard(self) -> List[Dict]:
        """
        Retrieve noticeboard items
        
        Returns:
            List of noticeboard items
        """
        if not self.auth_token:
            logger.warning("Not authenticated. Call login() first.")
            return []
        
        try:
            url = f"{self.base_url}/students/noticeboard"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            logger.info(f"Retrieved {len(items)} noticeboard items")
            return items
            
        except Exception as e:
            logger.error(f"Failed to get noticeboard: {e}")
            return []
    
    def download_attachment(self, attachment_id: str) -> Optional[bytes]:
        """
        Download attachment (e.g., PDF file)
        
        Args:
            attachment_id: ID of the attachment to download
            
        Returns:
            Attachment content as bytes, or None if failed
        """
        if not self.auth_token:
            logger.warning("Not authenticated. Call login() first.")
            return None
        
        try:
            url = f"{self.base_url}/students/noticeboard/attach/{attachment_id}"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            logger.info(f"Downloaded attachment {attachment_id}")
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to download attachment {attachment_id}: {e}")
            return None
    
    def mark_as_read(self, event_code: str) -> bool:
        """
        Mark a communication as read
        
        Args:
            event_code: Event code to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        if not self.auth_token:
            logger.warning("Not authenticated. Call login() first.")
            return False
        
        try:
            url = f"{self.base_url}/students/agenda/event/{event_code}/read"
            response = self.session.post(url, headers=self._get_headers())
            response.raise_for_status()
            
            logger.info(f"Marked event {event_code} as read")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark event {event_code} as read: {e}")
            return False
