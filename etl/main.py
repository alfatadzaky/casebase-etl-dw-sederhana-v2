import logging
import sys

from extract import extract

from transform.dim_produk import transform_dim_produk
from transform.dim_pelanggan import build_dim_pelanggan
from transform.dim_waktu import build_dim_waktu
from transform.dim_metode_bayar import build_dim_metode_bayar
from transform.fakta_penjualan import transform_fakta_penjualan

from load import load

# stream=sys.stdout agar urutan log dan tabel (print) tidak tertukar di terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

def judul(teks):
    """Cetak satu baris kosong lalu judul bagian, supaya output tidak mepet."""
    print()
    log.info("=== %s ===", teks)

def tampilkan(df):
    """Cetak 5 baris pertama dan jumlah baris sebuah tabel."""
    print(df.head().to_string(index=False))
    print(f"Jumlah baris: {len(df)}")

def main():
    log.info("===== MEMULAI ETL TOKOMAJU =====")

    # EXTRACT (judul "=== EXTRACT ===" dicetak di dalam extract())
    print()
    df_penjualan, df_produk, df_pelanggan = extract()

    # TRANSFORM
    judul("TRANSFORM")

    judul("DIMENSI PRODUK")
    dim_produk = transform_dim_produk(df_produk)
    tampilkan(dim_produk)

    judul("DIMENSI PELANGGAN")
    dim_pelanggan = build_dim_pelanggan(df_pelanggan)
    tampilkan(dim_pelanggan)

    judul("DIMENSI WAKTU")
    dim_waktu = build_dim_waktu(df_penjualan)
    tampilkan(dim_waktu)

    judul("DIMENSI METODE BAYAR")
    dim_metode_bayar = build_dim_metode_bayar(df_penjualan)
    tampilkan(dim_metode_bayar)

    judul("FAKTA PENJUALAN")
    fakta_penjualan, reject_fakta = transform_fakta_penjualan(
        df_penjualan,
        dim_pelanggan,
        dim_produk,
        dim_waktu,
        dim_metode_bayar
    )
    tampilkan(fakta_penjualan)

    judul("REJECT FAKTA PENJUALAN")
    tampilkan(reject_fakta)
    print("Ringkasan alasan ditolak:")
    print(reject_fakta["alasan_ditolak"].value_counts().to_string())

    # LOAD
    judul("LOAD")
    load(
        dim_produk,
        dim_pelanggan,
        dim_waktu,
        dim_metode_bayar,
        fakta_penjualan,
        reject_fakta
    )

    print()
    log.info("===== ETL TOKOMAJU SELESAI =====")

if __name__ == "__main__":
    main()