import logging
import pandas as pd

log = logging.getLogger(__name__)

def build_dim_metode_bayar(df_penjualan):
    """Membuat dimensi metode pembayaran dari nilai unik transaksi."""
    metode = (
        df_penjualan["metode_bayar"].astype("string").str.strip().str.upper()
    )
    metode = metode.replace("", pd.NA).dropna().drop_duplicates().sort_values()

    log.info("Ambil metode bayar unik: %d (%s)", len(metode), ", ".join(metode))

    dim = pd.DataFrame({"metode_bayar": metode.tolist()})
    dim.insert(0, "metode_bayar_key", range(1, len(dim) + 1))
    log.info("Buat surrogate key metode_bayar_key (+ baris default key 0)")

    baris_default = pd.DataFrame([{
        "metode_bayar_key": 0,
        "metode_bayar": "Tidak Diketahui",
    }])
    return pd.concat([baris_default, dim], ignore_index=True) 