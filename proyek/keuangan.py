"""keuangan.py - Aplikasi 4: rekap pemasukan (denda, sewa) dan pengeluaran (beli buku, operasional).

Hasil operasi berupa tuple (True, data) atau (False, "pesan error").
State: tuple transaksi (immutable); setiap pencatatan mengembalikan tuple BARU.
Jalankan sendiri: python keuangan.py
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

import data
import fplib

ATURAN_TRANSAKSI = [
    (lambda d: d.get("tanggal") is not None, "Tanggal wajib diisi"),
    (lambda d: d.get("kategori") in data.KATEGORI_KEUANGAN, "Kategori tidak dikenal"),
    (lambda d: d.get("nominal", 0) > 0, "Nominal harus lebih dari 0"),
    (lambda d: len(d.get("keterangan", "")) >= 3, "Keterangan minimal 3 karakter"),
]


def catat(daftar: tuple, d: Dict[str, Any]):
    """Catat transaksi -> (True, (daftar_baru, record)) atau (False, pesan)."""
    galat = fplib.validate(d, ATURAN_TRANSAKSI)
    if galat:
        return (False, "; ".join(galat))
    rec = {"id": f"K{len(daftar) + 1:03d}", "tanggal": d["tanggal"],
           "jenis": "masuk" if d["kategori"] in data.KATEGORI_PEMASUKAN else "keluar",
           "kategori": d["kategori"], "nominal": d["nominal"], "keterangan": d["keterangan"]}
    return (True, (daftar + (rec,), rec))


def catat_dari_struk(daftar: tuple, struk: Dict[str, Any]):
    """Catat pembayaran dari struk Loket sebagai pemasukan."""
    return catat(daftar, {"tanggal": struk["tanggal"], "kategori": struk["jenis"], "nominal": struk["jumlah"],
                          "keterangan": f"Struk {struk['no']} anggota {struk['anggota_id']}"})


# ------------------------------------------------------------------- kueri
def transaksi_bulan(daftar: tuple, jenis: str, bulan: str) -> tuple:
    """Transaksi berjenis 'masuk'/'keluar' pada bulan 'YYYY-MM'."""
    return fplib.where(daftar, lambda t: t["jenis"] == jenis, lambda t: t["tanggal"].strftime("%Y-%m") == bulan)


def pengeluaran_terbesar(daftar: tuple, n: int) -> tuple:
    """n pengeluaran dengan nominal terbesar."""
    return fplib.sort_by(fplib.where(daftar, lambda t: t["jenis"] == "keluar"),
                         lambda t: t["nominal"], descending=True)[:n]


def rekap_per_kategori(daftar: tuple) -> Dict[str, int]:
    """Total nominal per kategori, urut nama kategori."""
    grup = fplib.group_by(daftar, lambda t: t["kategori"])
    return dict(fplib.sort_by(tuple((k, fplib.sum_by(v, lambda t: t["nominal"])) for k, v in grup.items()),
                              lambda kv: kv[0]))


def total_per_bulan(daftar: tuple) -> Dict[str, Dict[str, int]]:
    """Pemasukan, pengeluaran, dan saldo per bulan."""
    grup = fplib.group_by(daftar, lambda t: t["tanggal"].strftime("%Y-%m"))
    jumlah = lambda items, jenis: fplib.sum_by(fplib.where(items, lambda t: t["jenis"] == jenis), lambda t: t["nominal"])
    return {b: {"masuk": jumlah(v, "masuk"), "keluar": jumlah(v, "keluar"),
                "saldo": jumlah(v, "masuk") - jumlah(v, "keluar")} for b, v in sorted(grup.items())}


def _ringkas(daftar: tuple) -> Dict[str, Any]:
    """Langkah pipe 1: kumpulkan angka-angka laporan."""
    return {"kategori": rekap_per_kategori(daftar), "bulan": total_per_bulan(daftar),
            "terbesar": pengeluaran_terbesar(daftar, 2),
            "saldo": fplib.sum_by(daftar, lambda t: t["nominal"] if t["jenis"] == "masuk" else -t["nominal"])}


def _susun_teks(r: Dict[str, Any]) -> str:
    """Langkah pipe 2: ubah ringkasan menjadi teks laporan."""
    rp = fplib.format_rupiah
    baris = (("Rekap per kategori:",)
             + tuple(f"  {k:<12}: {rp(v)}" for k, v in r["kategori"].items())
             + ("Total per bulan:",)
             + tuple(f"  {b}  masuk {rp(v['masuk'])} | keluar {rp(v['keluar'])} | saldo {rp(v['saldo'])}"
                     for b, v in r["bulan"].items())
             + ("2 pengeluaran terbesar:",)
             + tuple(f"  {t['kategori']:<12}: {rp(t['nominal'])} ({t['keterangan']})" for t in r["terbesar"])
             + (f"Saldo akhir: {rp(r['saldo'])}",))
    return "\n".join(baris)


def laporan(daftar: tuple) -> str:
    """Alur pembuatan laporan: ringkas -> susun teks."""
    return fplib.pipe(daftar, _ringkas, _susun_teks)


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 4: KEUANGAN\n", "=" * 50, sep="")
    s0 = data.TRANSAKSI_AWAL
    print("[BERHASIL] Catat pembelian buku Rp175.000")
    _, (s1, rec) = catat(s0, {"tanggal": date(2026, 11, 10), "kategori": "beli_buku",
                              "nominal": 175000, "keterangan": "Buku baru semester genap"})
    print(f"  Tercatat {rec['id']} ({rec['jenis']})")
    print("[GAGAL] Kategori tidak dikenal :", catat(s1, {"tanggal": date(2026, 11, 10), "kategori": "hadiah",
                                                         "nominal": 1000, "keterangan": "uji coba"}))
    print("[GAGAL] Nominal negatif        :", catat(s1, {"tanggal": date(2026, 11, 10), "kategori": "sewa",
                                                         "nominal": -5, "keterangan": "uji coba"}))
    print("\nPengeluaran Nov 2026:", tuple(map(lambda t: (t["kategori"], fplib.format_rupiah(t["nominal"])),
                                              transaksi_bulan(s1, "keluar", "2026-11"))))
    print()
    print(laporan(s1))
