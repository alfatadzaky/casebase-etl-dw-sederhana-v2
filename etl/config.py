import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Membaca konfigurasi dari file .env di folder utama project
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = Path(__file__).resolve().parent / "data"
CSV_PATH = DATA_DIR / "penjualan.csv"
XLSX_PATH = DATA_DIR / "produk.xlsx"

DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD_SOURCE = quote_plus(os.getenv("DB_PASSWORD_SOURCE", ""))
DB_PASSWORD_TARGET = quote_plus(os.getenv("DB_PASSWORD_TARGET", ""))
DB_HOST = os.getenv("DB_HOST", "localhost")
SOURCE_PORT = os.getenv("SOURCE_PORT", "5432")
TARGET_PORT = os.getenv("TARGET_PORT", "5432")
SOURCE_DB = os.getenv("SOURCE_DB", "")
TARGET_DB = os.getenv("TARGET_DB", "")

def buat_url(user, password, host, port, database):
    if not all([user, database]):
        raise ValueError("Konfigurasi DB_USER dan nama database belum diisi di file .env.")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

SOURCE_URL = buat_url(DB_USER, DB_PASSWORD_SOURCE, DB_HOST, SOURCE_PORT, SOURCE_DB)
TARGET_URL = buat_url(DB_USER, DB_PASSWORD_TARGET, DB_HOST, TARGET_PORT, TARGET_DB)
