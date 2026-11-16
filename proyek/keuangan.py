"""keuangan.py - Aplikasi 4: rekap pemasukan (denda, sewa) dan pengeluaran.

State: tuple transaksi (immutable). Setiap pencatatan mengembalikan tuple baru.
"""
from typing import Any, Dict

from data import KATEGORI_PEMASUKAN, KATEGORI_PENGELUARAN
from fplib import (Result, compose, err, flat_map, format_rupiah, group_by,
                   in_range, map_result, ok, pipe, required, sum_by,
                   min_length, validate)


def _kategori_valid(data) -> Result:
    """Rule khusus: kategori harus salah satu kategori yang dikenal."""
    semua = KATEGORI_PEMASUKAN | KATEGORI_PENGELUARAN
    return ok(data) if data.get("kategori") in semua else err(f"Kategori '{data.get('kategori')}' tidak dikenal")


validasi_transaksi = validate(
    required("tanggal"), required("kategori"), _kategori_valid,
    in_range("nominal", 1, 1_000_000_000), min_length("keterangan", 3),
)


def _cek_duplikat(daftar: tuple):
    """Rule: tolak transaksi yang identik (mencegah pencatatan ganda)."""
    kunci = lambda t: (t["tanggal"], t["kategori"], t["nominal"], t["keterangan"])
    return lambda d: (
        err("Transaksi duplikat, sudah pernah dicatat")
        if any(map(lambda t: kunci(t) == kunci(d), daftar))
        else ok(d))


def _buat_transaksi(daftar, d) -> tuple:
    """Bentuk record transaksi dan tuple baru."""
    rec = {"id": f"K{len(daftar) + 1:03d}", "tanggal": d["tanggal"],
           "jenis": "masuk" if d["kategori"] in KATEGORI_PEMASUKAN else "keluar",
           "kategori": d["kategori"], "nominal": d["nominal"], "keterangan": d["keterangan"]}
    return (daftar + (rec,), rec)


def catat(daftar: tuple, data: Dict[str, Any]) -> Result:
    """Catat transaksi -> ok((daftar_baru, record)) atau err(pesan)."""
    return pipe(
        data,
        validasi_transaksi,
        lambda r: flat_map(r, _cek_duplikat(daftar)),
        lambda r: map_result(r, lambda d: _buat_transaksi(daftar, d)),
    )


def catat_dari_struk(daftar: tuple, struk: Dict[str, Any]) -> Result:
    """Catat pembayaran dari struk Loket sebagai pemasukan."""
    return catat(daftar, {"tanggal": struk["tanggal"], "kategori": struk["jenis"],
                          "nominal": struk["jumlah"],
                          "keterangan": f"Struk {struk['no']} anggota {struk['anggota_id']}"})


# compose: kelompokkan per kategori, lalu jumlahkan nominalnya
rekap_per_kategori = compose(
    lambda grup: {k: sum_by(v, lambda t: t["nominal"]) for k, v in sorted(grup.items())},
    lambda daftar: group_by(daftar, lambda t: t["kategori"]),
)


def total_per_bulan(daftar: tuple) -> Dict[str, Dict[str, int]]:
    """Pemasukan, pengeluaran, dan saldo per bulan (format YYYY-MM)."""
    grup = group_by(daftar, lambda t: t["tanggal"].strftime("%Y-%m"))
    total = lambda items, jenis: sum_by(filter(lambda t: t["jenis"] == jenis, items), lambda t: t["nominal"])
    return {b: {"masuk": total(v, "masuk"), "keluar": total(v, "keluar"),
                "saldo": total(v, "masuk") - total(v, "keluar")}
            for b, v in sorted(grup.items())}


def laporan(daftar: tuple) -> str:
    """Hasilkan teks laporan keuangan."""
    kategori = tuple(map(lambda kv: f"  {kv[0]:<12}: {format_rupiah(kv[1])}", rekap_per_kategori(daftar).items()))
    bulan = tuple(map(
        lambda kv: f"  {kv[0]}  masuk {format_rupiah(kv[1]['masuk'])} | keluar {format_rupiah(kv[1]['keluar'])}"
                   f" | saldo {format_rupiah(kv[1]['saldo'])}",
        total_per_bulan(daftar).items()))
    saldo = sum_by(daftar, lambda t: t["nominal"] if t["jenis"] == "masuk" else -t["nominal"])
    return "\n".join(("Rekap per kategori:",) + kategori + ("Total per bulan:",) + bulan
                     + (f"Saldo akhir: {format_rupiah(saldo)}",))
