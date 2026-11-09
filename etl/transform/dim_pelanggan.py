import logging
import re
import pandas as pd

log = logging.getLogger(__name__)

# Singkatan / penulisan lain yang disatukan ke nama kota baku 
KOTA_PETA = {
    "Mlg": "Malang",
    "Sby": "Surabaya",
    "Sda": "Sidoarjo",
    "Dki Jakarta": "Jakarta",
}

def normalisasi_telepon(nilai):
    if pd.isna(nilai):
        return pd.NA

    digit = re.sub(r"\D", "", str(nilai))
    if digit.startswith("62"):
        digit = digit[2:]
    elif digit.startswith("0"):
        digit = digit[1:]
    digit = digit.lstrip("0")

    if not 8 <= len(digit) <= 13:
        return pd.NA
    return "+62" + digit

def build_dim_pelanggan(df_pelanggan):
    """Membersihkan master pelanggan dan membentuk surrogate key."""
    kolom = ["id_pelanggan", "nama", "kota", "telepon"]
    df = df_pelanggan[kolom].copy()
    log.info("Pelanggan dibaca: %d baris", len(df))

    df["id_pelanggan"] = (
        df["id_pelanggan"].astype("string").str.strip().str.upper()
    )
    df = df.replace({"": pd.NA, "NULL": pd.NA, "NONE": pd.NA, "NAN": pd.NA, "-": pd.NA})
    df = df.dropna(subset=["id_pelanggan"])

    n_sebelum = len(df)
    df = df.drop_duplicates(subset=["id_pelanggan"]).sort_values("id_pelanggan")
    log.info("Hapus duplikat id_pelanggan: %d baris", n_sebelum - len(df))

    df["nama_pelanggan"] = (
        df["nama"].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        .str.title().fillna("Tanpa Nama")
    )

    variasi_awal = df["kota"].dropna().nunique()
    df["kota"] = (
        df["kota"].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        .str.title()
        .str.replace(r"^Kota\s+", "", regex=True)   # "Kota Malang" -> "Malang"
        .replace(KOTA_PETA)                          # "Mlg" -> "Malang", dst.
        .fillna("Tidak Diketahui")
    )
    df["kota"] = df["kota"].replace("", "Tidak Diketahui")
    log.info("Seragamkan nama kota: %d variasi penulisan -> %d kota",
             variasi_awal, df.loc[df["kota"] != "Tidak Diketahui", "kota"].nunique())
    log.info("Isi kota kosong dengan 'Tidak Diketahui'")

    df["telepon"] = df["telepon"].apply(normalisasi_telepon)
    log.info("Seragamkan format telepon ke +62")

    df.insert(0, "pelanggan_key", range(1, len(df) + 1))
    log.info("Buat surrogate key pelanggan_key")
    dim = df[["pelanggan_key", "id_pelanggan", "nama_pelanggan", "kota", "telepon"]]

    baris_default = pd.DataFrame([{
        "pelanggan_key": 0,
        "id_pelanggan": "-",
        "nama_pelanggan": "Tidak Diketahui",
        "kota": "Tidak Diketahui",
        "telepon": pd.NA,
    }])
    return pd.concat([baris_default, dim], ignore_index=True)