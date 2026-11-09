import logging
from sqlalchemy import create_engine, text

from config import TARGET_URL

log = logging.getLogger(__name__)

def load(dim_produk, dim_pelanggan, dim_waktu, dim_metode_bayar,
         fakta_penjualan, reject_fakta):
    """Memuat ulang seluruh tabel DW (termasuk tabel reject) dan membuat primary/foreign key."""
    engine = create_engine(TARGET_URL)

    try:
        with engine.begin() as conn:
            # Hapus tabel lama dari fakta ke dimensi agar tidak melanggar FK
            conn.execute(text("DROP TABLE IF EXISTS reject_fakta_penjualan"))
            conn.execute(text("DROP TABLE IF EXISTS fakta_penjualan"))
            conn.execute(text("DROP TABLE IF EXISTS dim_metode_bayar"))
            conn.execute(text("DROP TABLE IF EXISTS dim_waktu"))
            conn.execute(text("DROP TABLE IF EXISTS dim_produk"))
            conn.execute(text("DROP TABLE IF EXISTS dim_pelanggan"))

            # Buat tabel dan isi data
            for nama, df in [
                ("dim_pelanggan", dim_pelanggan),
                ("dim_produk", dim_produk),
                ("dim_waktu", dim_waktu),
                ("dim_metode_bayar", dim_metode_bayar),
                ("fakta_penjualan", fakta_penjualan),
                ("reject_fakta_penjualan", reject_fakta),
            ]:
                df.to_sql(nama, conn, if_exists="replace", index=False)
                jumlah = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{nama}"')
                ).scalar_one()
                if jumlah != len(df):
                    raise ValueError(f"Jumlah data tabel {nama} tidak sesuai.")
                log.info("%s berhasil dimuat: %d baris", nama, jumlah)

            # Primary key dimensi
            conn.execute(text("ALTER TABLE dim_pelanggan ADD PRIMARY KEY (pelanggan_key)"))
            conn.execute(text("ALTER TABLE dim_produk ADD PRIMARY KEY (produk_key)"))
            conn.execute(text("ALTER TABLE dim_waktu ADD PRIMARY KEY (waktu_key)"))
            conn.execute(text("ALTER TABLE dim_metode_bayar ADD PRIMARY KEY (metode_bayar_key)"))

            # Primary key fakta dan relasi ke dimensi
            conn.execute(text(
                "ALTER TABLE fakta_penjualan "
                "ADD PRIMARY KEY (id_transaksi, produk_key)"
            ))
            conn.execute(text("""
                ALTER TABLE fakta_penjualan
                ADD CONSTRAINT fk_fakta_pelanggan
                    FOREIGN KEY (pelanggan_key) REFERENCES dim_pelanggan(pelanggan_key),
                ADD CONSTRAINT fk_fakta_produk
                    FOREIGN KEY (produk_key) REFERENCES dim_produk(produk_key),
                ADD CONSTRAINT fk_fakta_waktu
                    FOREIGN KEY (waktu_key) REFERENCES dim_waktu(waktu_key),
                ADD CONSTRAINT fk_fakta_metode_bayar
                    FOREIGN KEY (metode_bayar_key) REFERENCES dim_metode_bayar(metode_bayar_key)
            """))

        log.info("Seluruh data berhasil dimuat ke Data Warehouse.")
    finally:
        engine.dispose()