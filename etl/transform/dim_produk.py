import logging
import pandas as pd

log = logging.getLogger(__name__)

def transform_dim_produk(df_produk):
    """Membersihkan master produk dan membentuk surrogate key."""
    kolom = ["id_produk", "nama_produk", "kategori", "merek"]
    df = df_produk[kolom].copy()
    log.info("Produk dibaca: %d baris", len(df))

    for kolom in kolom:
        df[kolom] = df[kolom].astype("string").str.strip()

    df = df.replace("", pd.NA)
    df["id_produk"] = df["id_produk"].str.upper()
    df = df.dropna(subset=["id_produk"])

    n_sebelum = len(df)
    df = df.drop_duplicates(subset=["id_produk"]).sort_values("id_produk")
    log.info("Hapus duplikat id_produk: %d baris", n_sebelum - len(df))

    mapping_kategori = {
        "mamin": "Makanan & Minuman",
        "makanan & minuman": "Makanan & Minuman",
        "rumah tangga": "Rumah Tangga",
        "elektronik": "Elektronik",
        "fashion": "Fashion",
        "olahraga": "Olahraga",
        "kesehatan & kecantikan": "Kesehatan & Kecantikan",
        "kesehatan dan kecantikan": "Kesehatan & Kecantikan",
    }
    variasi_awal = df["kategori"].nunique()
    kategori_bersih = df["kategori"].str.lower()
    df["kategori"] = kategori_bersih.map(mapping_kategori).fillna(
        df["kategori"].str.title()
    )
    log.info("Seragamkan kategori: %d variasi penulisan -> %d kategori",
             variasi_awal, df["kategori"].nunique())

    kosong = ", ".join(
        f"{k}={int(df[k].isna().sum())}" for k in ["nama_produk", "kategori", "merek"]
    )
    for kolom in ["nama_produk", "kategori", "merek"]:
        df[kolom] = df[kolom].fillna("Tidak Diketahui")
    log.info("Isi nilai kosong dengan 'Tidak Diketahui': %s", kosong)

    df.insert(0, "produk_key", range(1, len(df) + 1))
    log.info("Buat surrogate key produk_key")

    baris_default = pd.DataFrame([{
        "produk_key": 0,
        "id_produk": "-",
        "nama_produk": "Tidak Diketahui",
        "kategori": "Tidak Diketahui",
        "merek": "Tidak Diketahui",
    }])

    return pd.concat([baris_default, df], ignore_index=True)[
        ["produk_key", "id_produk", "nama_produk", "kategori", "merek"]
    ]