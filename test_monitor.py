#!/usr/bin/env python3
"""
Test script for monitor.py components
"""

import sys
import json
from datetime import datetime
import pytz

# Import components from monitor
from monitor import (
    log_colored,
    TelegramNotifier,
    ClasseVivaMonitor,
    load_state,
    save_state,
    ITALIAN_TZ
)
from colorama import Fore

def test_logging():
    """Test colored logging"""
    print("\n=== Testing Colored Logging ===")
    log_colored("INFO: Test info message", Fore.CYAN)
    log_colored("LOGIN: Test login message", Fore.GREEN)
    log_colored("ERRORE: Test error message", Fore.RED)
    log_colored("INFO: Test warning message", Fore.YELLOW)
    print("✓ Logging test passed")

def test_timezone():
    """Test Italian timezone"""
    print("\n=== Testing Italian Timezone ===")
    now = datetime.now(ITALIAN_TZ)
    timestamp = now.strftime('[%Y-%m-%d %H:%M:%S]')
    print(f"Current Italian time: {timestamp}")
    print("✓ Timezone test passed")

def test_state_management():
    """Test state save/load"""
    print("\n=== Testing State Management ===")
    
    # Create test state
    test_state = {
        'sent_hashes': ['hash1', 'hash2', 'hash3'],
        'last_check': '2025-01-15 10:00:00'
    }
    
    # Save state
    save_state(test_state)
    print("✓ State saved")
    
    # Load state
    loaded_state = load_state()
    print(f"✓ State loaded: {len(loaded_state.get('sent_hashes', []))} hashes")
    
    assert loaded_state['sent_hashes'] == test_state['sent_hashes'], "State mismatch!"
    print("✓ State management test passed")

def test_telegram_notifier():
    """Test TelegramNotifier class initialization"""
    print("\n=== Testing TelegramNotifier ===")
    
    notifier = TelegramNotifier("test_token", "test_chat_id")
    assert notifier.bot_token == "test_token"
    assert notifier.chat_id == "test_chat_id"
    assert notifier.base_url == "https://api.telegram.org/bottest_token"
    print("✓ TelegramNotifier initialization passed")
    
    # Test message formatting
    test_comm = {
        'evtText': 'Test Communication',
        'evtDatetimeBegin': '2025-01-15 10:00:00',
        'notes': 'This is a test message for class 1AA and 2BC'
    }
    
    classes = {'1AA', '2BC'}
    message = notifier.format_communication(test_comm, classes)
    
    assert 'Test Communication' in message
    assert '1AA' in message
    assert '2BC' in message
    assert '📚' in message
    print("✓ Message formatting test passed")

def test_classeviva_monitor():
    """Test ClasseVivaMonitor class initialization"""
    print("\n=== Testing ClasseVivaMonitor ===")
    
    monitor = ClasseVivaMonitor("test@example.com", "testpass")
    assert monitor.username == "test@example.com"
    assert monitor.password == "testpass"
    assert monitor.session is None  # Not logged in yet
    print("✓ ClasseVivaMonitor initialization passed")

def test_attachment_parsing():
    """Test attachment parsing logic"""
    print("\n=== Testing Attachment Parsing ===")
    
    monitor = ClasseVivaMonitor("test@example.com", "testpass")
    
    # Test with direct allegati field
    comm1 = {
        'allegati': [
            {'allegato_id': '123', 'filename': 'test.pdf'},
            {'allegato_id': '456', 'filename': 'test2.pdf'}
        ]
    }
    
    attachments1 = monitor.parse_attachments(comm1)
    assert len(attachments1) == 2
    assert attachments1[0]['id'] == '123'
    assert attachments1[1]['filename'] == 'test2.pdf'
    print("✓ Direct allegati parsing passed")
    
    # Test with HTML parsing
    comm2 = {
        'notes': '<a href="download.php?allegato_id=789">Download PDF</a>'
    }
    
    attachments2 = monitor.parse_attachments(comm2)
    assert len(attachments2) == 1
    assert attachments2[0]['id'] == '789'
    print("✓ HTML allegati parsing passed")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  Monitor.py Component Tests")
    print("=" * 60)
    
    try:
        test_logging()
        test_timezone()
        test_state_management()
        test_telegram_notifier()
        test_classeviva_monitor()
        test_attachment_parsing()
        
        print("\n" + "=" * 60)
        print("  ✓ ALL TESTS PASSED")
        print("=" * 60)
        print()
        
        return 0
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
