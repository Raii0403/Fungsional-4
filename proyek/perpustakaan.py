"""perpustakaan.py - Aplikasi 1: peminjaman, pengembalian, dan denda.

Hasil operasi berupa tuple (True, data) atau (False, "pesan error").
State: {"buku", "anggota", "peminjaman"}; setiap operasi mengembalikan state BARU.
Jalankan sendiri: python perpustakaan.py
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

import data
import fplib

ATURAN_PEMINJAMAN = [
    (lambda d: d.get("anggota_id", "") != "", "ID anggota wajib diisi"),
    (lambda d: d.get("buku_id", "") != "", "ID buku wajib diisi"),
    (lambda d: d.get("tgl_pinjam") is not None, "Tanggal pinjam wajib diisi"),
    (lambda d: 1 <= d.get("lama_hari", 0) <= 14, "Lama pinjam harus 1-14 hari"),
]


# ------------------------------------------------------------------- kueri
def cari_buku(daftar, buku_id: str):
    """Cari buku berdasarkan ID; None jika tidak ada."""
    return fplib.find_by(daftar, lambda b: b["id"] == buku_id)


def buku_tersedia_kategori(daftar, nama: str) -> tuple:
    """Buku yang tersedia DAN berkategori nama."""
    return fplib.where(daftar, lambda b: b["status"] == "tersedia", lambda b: b["kategori"] == nama)


def katalog_urut(daftar) -> tuple:
    """Katalog terurut berdasarkan judul."""
    return fplib.sort_by(daftar, lambda b: b["judul"])


def buku_per_kategori(daftar) -> Dict[str, tuple]:
    """Kelompokkan buku per kategori."""
    return fplib.group_by(daftar, lambda b: b["kategori"])


def total_denda_belum_lunas(tagihan, anggota_id: str) -> int:
    """Total denda anggota yang belum dibayar."""
    belum = fplib.where(tagihan, lambda t: t["jenis"] == "denda", lambda t: t["anggota_id"] == anggota_id,
                        lambda t: not t["lunas"])
    return fplib.sum_by(belum, lambda t: t["jumlah"])


# --------------------------------------------------------------- peminjaman
def pinjam(state: Dict[str, Any], d: Dict[str, Any]):
    """Proses peminjaman -> (True, (state_baru, record)) atau (False, pesan)."""
    galat = fplib.validate(d, ATURAN_PEMINJAMAN)
    if galat:
        return (False, "; ".join(galat))
    if fplib.find_by(state["anggota"], lambda a: a["id"] == d["anggota_id"]) is None:
        return (False, f"Anggota {d['anggota_id']} tidak ditemukan")
    buku = cari_buku(state["buku"], d["buku_id"])
    if buku is None:
        return (False, f"Buku {d['buku_id']} tidak ditemukan")
    if buku["status"] != "tersedia":
        return (False, f"Buku '{buku['judul']}' sedang dipinjam")
    rec = {"id": f"P{len(state['peminjaman']) + 1:03d}", "anggota_id": d["anggota_id"], "buku_id": buku["id"],
           "tgl_pinjam": d["tgl_pinjam"], "tgl_jatuh_tempo": d["tgl_pinjam"] + timedelta(days=d["lama_hari"]),
           "tgl_kembali": None}
    state_baru = {**state, "peminjaman": state["peminjaman"] + (rec,),
                  "buku": fplib.update_where(state["buku"], lambda b: b["id"] == buku["id"], {"status": "dipinjam"})}
    return (True, (state_baru, rec))


def hitung_denda(tgl_jatuh_tempo: date, tgl_kembali: date) -> Dict[str, Any]:
    """Alur pipe: selisih hari -> hari telat -> denda -> teks rupiah."""
    return fplib.pipe(
        (tgl_jatuh_tempo, tgl_kembali),
        lambda t: fplib.diff_days(t[0], t[1]),
        lambda selisih: max(0, selisih),
        lambda telat: {"hari_telat": telat, "denda": telat * data.DENDA_PER_HARI},
        lambda info: {**info, "teks": fplib.format_rupiah(info["denda"])},
    )


def kembalikan(state: Dict[str, Any], peminjaman_id: str, tgl_kembali: date):
    """Proses pengembalian -> (True, (state_baru, info, tagihan_atau_None)) atau (False, pesan)."""
    p = fplib.find_by(state["peminjaman"], lambda x: x["id"] == peminjaman_id)
    if p is None or p["tgl_kembali"] is not None:
        return (False, f"Peminjaman {peminjaman_id} tidak ditemukan atau sudah dikembalikan")
    info = hitung_denda(p["tgl_jatuh_tempo"], tgl_kembali)
    tagihan = {"id": f"TGH-{p['id']}-D", "jenis": "denda", "anggota_id": p["anggota_id"],
               "jumlah": info["denda"], "tanggal": tgl_kembali, "lunas": False,
               "keterangan": f"Denda telat {info['hari_telat']} hari ({p['buku_id']})"} if info["denda"] > 0 else None
    state_baru = {**state,
                  "peminjaman": fplib.update_where(state["peminjaman"], lambda x: x["id"] == peminjaman_id,
                                                   {"tgl_kembali": tgl_kembali}),
                  "buku": fplib.update_where(state["buku"], lambda b: b["id"] == p["buku_id"], {"status": "tersedia"})}
    return (True, (state_baru, info, tagihan))


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 1: PERPUSTAKAAN\n", "=" * 50, sep="")
    s0 = {"buku": data.BUKU, "anggota": data.ANGGOTA, "peminjaman": ()}
    judul = lambda daftar: tuple(map(lambda b: b["judul"], daftar))
    print("Katalog urut judul   :", judul(katalog_urut(data.BUKU)))
    print("Buku per kategori    :", {k: judul(v) for k, v in buku_per_kategori(data.BUKU).items()})
    print("Novel yang tersedia  :", judul(buku_tersedia_kategori(data.BUKU, "Novel")))
    print("Cari buku B999       :", cari_buku(data.BUKU, "B999"))
    print("Denda Budi (A002)    :", fplib.format_rupiah(total_denda_belum_lunas(data.TAGIHAN_AWAL, "A002")))

    print("\n[BERHASIL] Andi meminjam B001 pada 2026-11-01 (7 hari)")
    _, (s1, p1) = pinjam(s0, {"anggota_id": "A001", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 1), "lama_hari": 7})
    print(f"  {p1['id']}, jatuh tempo {p1['tgl_jatuh_tempo']}, status buku:", cari_buku(s1["buku"], "B001")["status"])
    print("[GAGAL] Citra meminjam B001 yang sedang dipinjam :", pinjam(s1, {"anggota_id": "A003", "buku_id": "B001",
          "tgl_pinjam": date(2026, 11, 3), "lama_hari": 7}))
    print("[GAGAL] Data tidak valid                          :", pinjam(s1, {"anggota_id": "", "buku_id": "B002",
          "tgl_pinjam": date(2026, 11, 3), "lama_hari": 30}))

    print("\n[BERHASIL] Andi mengembalikan 2026-11-11")
    _, (s2, info, tagihan) = kembalikan(s1, p1["id"], date(2026, 11, 11))
    print(f"  Telat {info['hari_telat']} hari, denda {info['teks']}, tagihan: {tagihan['id']}")
    print("[GAGAL] Dikembalikan dua kali :", kembalikan(s2, p1["id"], date(2026, 11, 12)))
