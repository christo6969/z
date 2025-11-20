"""
ClasseViva Monitor Bot
Telegram bot for monitoring ClasseViva notifications
Optimized for Raspberry Pi

Uses kurigram (pyrogram fork from kurimuzonakuma/pyrogram)
With colored console logging from local_monitor.py
"""

import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Import from kurigram (pyrogram fork)
from pyrogram import Client, filters
from pyrogram.types import Message

from config import API_ID, API_HASH, ENABLE_LOGGING, LOG_LEVEL, LOG_FILE, MAX_WORKERS
from classeviva_api import ClasseVivaAPI, log_colored
from class_detector import detect_classes

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

# Setup logging
if ENABLE_LOGGING:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables")

log_colored("INFO: Bot inizializzato", Fore.CYAN)

# Initialize Pyrogram client
app = Client(
    "classeviva_monitor_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=MAX_WORKERS
)

# ClasseViva API instance
classeviva_api: Optional[ClasseVivaAPI] = None


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    welcome_text = """
🎓 **Benvenuto in ClasseViva Monitor Bot**

Bot ottimizzato per Raspberry Pi che monitora le notifiche di ClasseViva.

**Comandi disponibili:**
/start - Mostra questo messaggio
/login - Accedi a ClasseViva
/check - Controlla nuove comunicazioni
/help - Mostra la guida

**Funzionalità:**
✅ Monitoraggio automatico delle comunicazioni
✅ Rilevamento automatico delle classi (formato: 1AA, 2BC, ecc.)
✅ Parsing di allegati PDF
✅ Ottimizzato per Raspberry Pi

Usa /login per iniziare!
    """
    await message.reply_text(welcome_text)


@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    help_text = """
📚 **Guida ClasseViva Monitor Bot**

**Comandi:**
/login - Accedi con le tue credenziali ClasseViva
/check - Controlla manualmente nuove comunicazioni
/status - Verifica lo stato della connessione
/logout - Disconnetti da ClasseViva

**Rilevamento Classi:**
Il bot rileva automaticamente le menzioni di classi nel formato:
- [numero 1-5][2 lettere maiuscole]
- Esempi: 1AA, 2BC, 3XY, 5ZZ

Le classi rilevate vengono mostrate in una riga separata nell'output.

**Supporto:**
Per problemi o domande, contatta l'amministratore.
    """
    await message.reply_text(help_text)


@app.on_message(filters.command("login"))
async def login_command(client: Client, message: Message):
    """Handle /login command"""
    global classeviva_api
    
    status_msg = await message.reply_text("🔄 Autenticazione in corso...")
    
    try:
        # Initialize API with hardcoded credentials
        classeviva_api = ClasseVivaAPI()
        
        if classeviva_api.login():
            await status_msg.edit_text("✅ Autenticazione riuscita!\nUsa /check per controllare le comunicazioni.")
            log_colored("TELEGRAM: Messaggio inviato (login riuscito)", Fore.GREEN)
        else:
            await status_msg.edit_text("❌ Autenticazione fallita. Verifica le credenziali.")
            log_colored("TELEGRAM: Messaggio inviato (login fallito)", Fore.RED)
            classeviva_api = None
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        log_colored(f"ERRORE: Login command fallito - {str(e)}", Fore.RED)
        await status_msg.edit_text(f"❌ Errore durante l'autenticazione: {str(e)}")
        classeviva_api = None


@app.on_message(filters.command("check"))
async def check_command(client: Client, message: Message):
    """Handle /check command - Check for new communications"""
    global classeviva_api
    
    if not classeviva_api:
        await message.reply_text("❌ Non sei autenticato. Usa /login prima.")
        return
    
    status_msg = await message.reply_text("🔄 Controllo comunicazioni...")
    log_colored("INFO: Controllo comunicazioni richiesto", Fore.CYAN)
    
    try:
        # Get communications
        communications = classeviva_api.get_communications()
        
        if not communications:
            await status_msg.edit_text("✅ Nessuna nuova comunicazione.")
            log_colored("TELEGRAM: Messaggio inviato (nessuna comunicazione)", Fore.GREEN)
            return
        
        await status_msg.edit_text(f"📨 Trovate {len(communications)} nuove comunicazioni!")
        log_colored(f"TELEGRAM: Messaggio inviato ({len(communications)} comunicazioni)", Fore.GREEN)
        
        # Process each communication
        for comm in communications[:5]:  # Limit to 5 for memory efficiency
            title = comm.get("evtText", comm.get("titolo", "Nessun titolo"))
            date = comm.get("evtDatetimeBegin", comm.get("data", "Data sconosciuta"))
            notes = comm.get("notes", comm.get("testo", ""))
            
            # Build message
            comm_text = f"📌 **{title}**\n"
            comm_text += f"📅 Data: {date}\n"
            
            if notes:
                comm_text += f"\n{notes}\n"
            
            # Detect classes in text
            all_text = f"{title} {notes}"
            classes_output = detect_classes(text=all_text)
            
            if classes_output:
                comm_text += classes_output
            
            await message.reply_text(comm_text)
            log_colored("TELEGRAM: Messaggio inviato", Fore.GREEN)
            await asyncio.sleep(0.5)  # Small delay to avoid flooding
    
    except Exception as e:
        logger.error(f"Check error: {e}")
        log_colored(f"ERRORE: Check command fallito - {str(e)}", Fore.RED)
        await status_msg.edit_text(f"❌ Errore durante il controllo: {str(e)}")


@app.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    """Handle /status command"""
    global classeviva_api
    
    if classeviva_api and classeviva_api.phpsessid and classeviva_api.webidentity:
        status = "✅ Connesso a ClasseViva"
    else:
        status = "❌ Non connesso. Usa /login"
    
    await message.reply_text(f"**Status:**\n{status}")
    log_colored(f"INFO: Status richiesto - {status}", Fore.CYAN)


@app.on_message(filters.command("logout"))
async def logout_command(client: Client, message: Message):
    """Handle /logout command"""
    global classeviva_api
    
    classeviva_api = None
    await message.reply_text("✅ Disconnesso da ClasseViva.")


@app.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    """Handle document uploads (for PDF class detection)"""
    document = message.document
    
    # Check if it's a PDF
    if not document.mime_type or "pdf" not in document.mime_type.lower():
        return
    
    status_msg = await message.reply_text("🔄 Analisi PDF in corso...")
    
    try:
        # Download PDF
        pdf_path = await message.download()
        
        # Read PDF content
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Clean up
        os.remove(pdf_path)
        
        # Detect classes
        classes_output = detect_classes(pdf_content=pdf_content)
        
        if classes_output:
            await status_msg.edit_text(f"✅ Analisi completata!{classes_output}")
        else:
            await status_msg.edit_text("✅ Analisi completata! Nessuna classe rilevata.")
    
    except Exception as e:
        logger.error(f"PDF processing error: {e}")
        await status_msg.edit_text(f"❌ Errore durante l'analisi del PDF: {str(e)}")


async def periodic_check():
    """Periodic background check for new communications"""
    global classeviva_api
    
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            if not classeviva_api:
                continue
            
            # This would send notifications to subscribed users
            # Implementation depends on user management system
            logger.info("Periodic check executed")
            
        except Exception as e:
            logger.error(f"Periodic check error: {e}")


def main():
    """Main entry point"""
    log_colored("INFO: Avvio ClasseViva Monitor Bot (Raspberry Pi optimized)", Fore.CYAN)
    log_colored(f"INFO: Utilizzo kurigram da kurimuzonakuma/pyrogram", Fore.CYAN)
    log_colored(f"INFO: API ID: {API_ID}", Fore.CYAN)
    logger.info("Starting ClasseViva Monitor Bot (Raspberry Pi optimized)")
    logger.info(f"Using kurigram from kurimuzonakuma/pyrogram")
    logger.info(f"API ID: {API_ID}")
    
    # Start the bot
    app.run()


if __name__ == "__main__":
    main()
