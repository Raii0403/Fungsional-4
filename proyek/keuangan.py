"""keuangan.py - Aplikasi 4: rekap pemasukan (denda, sewa) dan pengeluaran.

State: tuple transaksi (immutable). Setiap pencatatan mengembalikan tuple baru.
Jalankan sendiri: python keuangan.py
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

import data
import fplib


def _kategori_valid(d):
    """Rule khusus: kategori harus salah satu kategori yang dikenal."""
    semua = data.KATEGORI_PEMASUKAN | data.KATEGORI_PENGELUARAN
    return fplib.ok(d) if d.get("kategori") in semua else fplib.err(f"Kategori '{d.get('kategori')}' tidak dikenal")


validasi_transaksi = fplib.validate(
    fplib.required("tanggal"), fplib.required("kategori"), _kategori_valid,
    fplib.in_range("nominal", 1, 1_000_000_000), fplib.min_length("keterangan", 3),
)


# ------------------------------------------------------------------ predikat
def jenis(nama: str):
    """Pabrik predikat: transaksi berjenis 'masuk' atau 'keluar'."""
    return lambda t: t["jenis"] == nama


def di_bulan(bulan: str):
    """Pabrik predikat: transaksi pada bulan 'YYYY-MM'."""
    return lambda t: t["tanggal"].strftime("%Y-%m") == bulan


# ----------------------------------------------------------------- pencatatan
def _cek_duplikat(daftar):
    """Rule: tolak transaksi identik (mencegah pencatatan ganda)."""
    kunci = lambda t: (t["tanggal"], t["kategori"], t["nominal"], t["keterangan"])
    return lambda d: (fplib.err("Transaksi duplikat, sudah pernah dicatat")
                      if fplib.where(daftar, lambda t: kunci(t) == kunci(d)) else fplib.ok(d))


def _buat_transaksi(daftar, d) -> tuple:
    """Bentuk record transaksi dan tuple baru."""
    rec = {"id": f"K{len(daftar) + 1:03d}", "tanggal": d["tanggal"],
           "jenis": "masuk" if d["kategori"] in data.KATEGORI_PEMASUKAN else "keluar",
           "kategori": d["kategori"], "nominal": d["nominal"], "keterangan": d["keterangan"]}
    return (daftar + (rec,), rec)


def catat(daftar: tuple, d: Dict[str, Any]):
    """Catat transaksi -> ok((daftar_baru, record)) atau err(pesan)."""
    return fplib.pipe(
        d,
        validasi_transaksi,
        lambda r: fplib.flat_map(r, _cek_duplikat(daftar)),
        lambda r: fplib.map_result(r, lambda x: _buat_transaksi(daftar, x)),
    )


def catat_dari_struk(daftar: tuple, struk: Dict[str, Any]):
    """Catat pembayaran dari struk Loket sebagai pemasukan."""
    return catat(daftar, {"tanggal": struk["tanggal"], "kategori": struk["jenis"], "nominal": struk["jumlah"],
                          "keterangan": f"Struk {struk['no']} anggota {struk['anggota_id']}"})


# ---------------------------------------------------------------------- kueri
# compose: kelompokkan per kategori, lalu jumlahkan nominalnya (urut nama kategori)
rekap_per_kategori = fplib.compose(
    lambda grup: dict(fplib.sort_by(
        tuple(map(lambda kv: (kv[0], fplib.sum_by(kv[1], lambda t: t["nominal"])), grup.items())),
        lambda kv: kv[0])),
    lambda daftar: fplib.group_by(daftar, lambda t: t["kategori"]),
)


def total_per_bulan(daftar: tuple) -> Dict[str, Dict[str, int]]:
    """Pemasukan, pengeluaran, dan saldo per bulan (format YYYY-MM)."""
    grup = fplib.group_by(daftar, lambda t: t["tanggal"].strftime("%Y-%m"))
    total = lambda items, j: fplib.sum_by(fplib.where(items, jenis(j)), lambda t: t["nominal"])
    return {b: {"masuk": total(v, "masuk"), "keluar": total(v, "keluar"), "saldo": total(v, "masuk") - total(v, "keluar")}
            for b, v in sorted(grup.items())}


def transaksi_bulan(daftar: tuple, j: str, bulan: str) -> tuple:
    """Transaksi berjenis j pada bulan tertentu."""
    return fplib.where(daftar, fplib.and_(jenis(j), di_bulan(bulan)))


def pengeluaran_terbesar(daftar: tuple, n: int) -> tuple:
    """n pengeluaran dengan nominal terbesar."""
    return fplib.top_n(fplib.where(daftar, jenis("keluar")), lambda t: t["nominal"], n)


def laporan(daftar: tuple) -> str:
    """Hasilkan teks laporan keuangan."""
    kategori = tuple(map(lambda kv: f"  {kv[0]:<12}: {fplib.format_rupiah(kv[1])}", rekap_per_kategori(daftar).items()))
    bulan = tuple(map(
        lambda kv: f"  {kv[0]}  masuk {fplib.format_rupiah(kv[1]['masuk'])} | keluar {fplib.format_rupiah(kv[1]['keluar'])}"
                   f" | saldo {fplib.format_rupiah(kv[1]['saldo'])}",
        total_per_bulan(daftar).items()))
    top = tuple(map(lambda t: f"  {t['kategori']:<12}: {fplib.format_rupiah(t['nominal'])} ({t['keterangan']})",
                    pengeluaran_terbesar(daftar, 2)))
    saldo = fplib.sum_by(daftar, lambda t: t["nominal"] if t["jenis"] == "masuk" else -t["nominal"])
    return "\n".join(("Rekap per kategori:",) + kategori + ("Total per bulan:",) + bulan
                     + ("2 pengeluaran terbesar:",) + top + (f"Saldo akhir: {fplib.format_rupiah(saldo)}",))


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 4: KEUANGAN\n", "=" * 50, sep="")
    s0 = data.TRANSAKSI_AWAL
    print("[BERHASIL] Catat pembelian buku Rp175.000")
    _, (s1, rec) = catat(s0, {"tanggal": date(2026, 11, 10), "kategori": "beli_buku",
                              "nominal": 175000, "keterangan": "Buku baru semester genap"})
    print(f"  Tercatat {rec['id']} ({rec['jenis']})")
    print("[GAGAL] Kategori tidak dikenal :", catat(s1, {"tanggal": date(2026, 11, 10), "kategori": "hadiah",
                                                         "nominal": 1000, "keterangan": "uji"}))
    print("[GAGAL] Nominal negatif        :", catat(s1, {"tanggal": date(2026, 11, 10), "kategori": "sewa",
                                                         "nominal": -5, "keterangan": "uji"}))
    print("[GAGAL] Transaksi dobel        :", catat(s1, {"tanggal": date(2026, 11, 10), "kategori": "beli_buku",
                                                         "nominal": 175000, "keterangan": "Buku baru semester genap"}))
    print("\nPengeluaran Nov 2026:", tuple(map(lambda t: (t["kategori"], fplib.format_rupiah(t["nominal"])),
                                              transaksi_bulan(s1, "keluar", "2026-11"))))
    print()
    print(laporan(s1))
