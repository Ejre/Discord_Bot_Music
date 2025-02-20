import logging
import pandas as pd
import os

# Pastikan folder logs ada
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "bot_requests.log")
EXCEL_FILE = os.path.join(LOG_DIR, "bot_requests.xlsx")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_request(message):
    """Mencatat request user ke dalam log file."""
    logging.info(message)

def export_log_to_excel():
    """Mengubah log file menjadi file Excel sebelum bot dimatikan."""
    try:
        if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
            print("🚫 No log file found or log is empty!")
            return

        logs = []
        with open(LOG_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(" - ", 2)
                if len(parts) == 3:
                    timestamp, level, message = parts
                    logs.append([timestamp, level, message])

        df = pd.DataFrame(logs, columns=["Timestamp", "Level", "Message"])
        df.to_excel(EXCEL_FILE, index=False)

        print(f"✅ Log berhasil diekspor ke {EXCEL_FILE}")

    except Exception as e:
        print(f"⚠ Error exporting log: {str(e)}")
