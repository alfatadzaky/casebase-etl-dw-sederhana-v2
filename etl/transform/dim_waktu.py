import logging
import re
import pandas as pd

log = logging.getLogger(__name__)

HARI = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu"
}
BULAN = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
BULAN_SINGKAT = { 
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "may": 5,
    "jun": 6, "jul": 7, "agu": 8, "aug": 8, "sep": 9,
    "okt": 10, "oct": 10, "nov": 11, "des": 12, "dec": 12
}

def parse_tanggal(nilai):
    """Mengenali yyyy-mm-dd, dd/mm/yyyy, dd-mm-yyyy, dan dd Mon yyyy."""
    if pd.isna(nilai):
        return pd.NaT

    teks = str(nilai).strip()
    try:
        cocok = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", teks)
        if cocok:
            return pd.Timestamp(int(cocok[1]), int(cocok[2]), int(cocok[3]))

        cocok = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", teks)
        if cocok:
            return pd.Timestamp(int(cocok[3]), int(cocok[2]), int(cocok[1]))

        cocok = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", teks)
        if cocok:
            bulan = BULAN_SINGKAT.get(cocok[2][:3].lower())
            if bulan:
                return pd.Timestamp(int(cocok[3]), bulan, int(cocok[1]))
    except ValueError:
        return pd.NaT

    return pd.NaT

def tanggal_ke_key(tanggal):
    return (
        tanggal.dt.year * 10000
        + tanggal.dt.month * 100
        + tanggal.dt.day
    ).astype("Int64")

def build_dim_waktu(df_penjualan):
    tanggal = pd.to_datetime(df_penjualan["tanggal"].apply(parse_tanggal))
    log.info("Seragamkan format tanggal: %d baris dibaca, %d tidak terbaca",
             len(tanggal), int(tanggal.isna().sum()))
    tanggal_unik = tanggal.dropna().dt.normalize().drop_duplicates().sort_values()

    dim = tanggal_unik.to_frame("tanggal").reset_index(drop=True)
    dim["waktu_key"] = tanggal_ke_key(dim["tanggal"]).astype(int)
    log.info("Buat surrogate key waktu_key")
    dim["hari"] = dim["tanggal"].dt.weekday.map(HARI)
    dim["bulan"] = dim["tanggal"].dt.month.map(BULAN)
    dim["kuartal"] = "Q" + dim["tanggal"].dt.quarter.astype(str)
    dim["tahun"] = dim["tanggal"].dt.year.astype(int)
    dim["tanggal"] = dim["tanggal"].dt.date 

    log.info("Ambil tanggal unik: %d hari (%s sampai %s)",
             len(dim), dim["tanggal"].min(), dim["tanggal"].max())

    return dim[["waktu_key", "tanggal", "hari", "bulan", "kuartal", "tahun"]]