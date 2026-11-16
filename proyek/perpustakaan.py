"""perpustakaan.py - Aplikasi 1: peminjaman, pengembalian, dan denda.

State: {"buku", "anggota", "peminjaman"}. Setiap operasi mengembalikan state BARU.
Jalankan sendiri: python perpustakaan.py
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

import data
import fplib

validasi_peminjaman = fplib.validate(
    fplib.required("anggota_id"), fplib.min_length("anggota_id", 4),
    fplib.required("buku_id"), fplib.required("tgl_pinjam"),
    fplib.in_range("lama_hari", 1, 14),
)


# ----------------------------------------------------------- predikat & cari
def tersedia(buku: Dict[str, Any]) -> bool:
    """Predikat: buku berstatus tersedia."""
    return buku["status"] == "tersedia"


def kategori(nama: str):
    """Pabrik predikat: buku berkategori tertentu."""
    return lambda b: b["kategori"] == nama


def _cari(daftar, id_: str):
    """Option item ber-ID tertentu."""
    hasil = fplib.where(daftar, lambda x: x["id"] == id_)
    return fplib.some(hasil[0]) if hasil else fplib.none()


def cari_buku(daftar, buku_id: str):
    """Cari buku berdasarkan ID; Option karena buku mungkin tidak ada."""
    return _cari(daftar, buku_id)


def cari_anggota(daftar, anggota_id: str):
    """Cari anggota berdasarkan ID; Option."""
    return _cari(daftar, anggota_id)


def cari_peminjaman(daftar, peminjaman_id: str):
    """Cari peminjaman berdasarkan ID; Option."""
    return _cari(daftar, peminjaman_id)


# ------------------------------------------------------------- kueri buku
def buku_tersedia_kategori(daftar, nama: str) -> tuple:
    """Buku yang tersedia DAN berkategori nama."""
    return fplib.where(daftar, fplib.and_(tersedia, kategori(nama)))


def buku_dipinjam(daftar) -> tuple:
    """Buku yang TIDAK tersedia (sedang dipinjam)."""
    return fplib.where(daftar, fplib.not_(tersedia))


def buku_terpopuler(daftar, n: int) -> tuple:
    """n buku dengan jumlah peminjaman terbanyak."""
    return fplib.top_n(daftar, lambda b: b["jumlah_pinjam"], n)


def buku_urut_judul(daftar) -> tuple:
    """Katalog terurut berdasarkan judul."""
    return fplib.sort_by(daftar, lambda b: b["judul"])


def buku_per_kategori(daftar) -> Dict[str, tuple]:
    """Kelompokkan buku per kategori."""
    return fplib.group_by(daftar, lambda b: b["kategori"])


# compose: kelompokkan per kategori, lalu hitung jumlah buku tiap kategori
jumlah_buku_per_kategori = fplib.compose(
    lambda grup: {k: fplib.sum_by(v, lambda _: 1) for k, v in grup.items()},
    buku_per_kategori,
)


# ------------------------------------------------------------- peminjaman
def _cek_anggota(state):
    """Rule: anggota harus terdaftar."""
    def rule(d):
        a = fplib.get_or_else(cari_anggota(state["anggota"], d["anggota_id"]), None)
        return fplib.ok(d) if a else fplib.err(f"Anggota {d['anggota_id']} tidak ditemukan")
    return rule


def _cek_tersedia(state):
    """Rule: buku harus ada dan berstatus tersedia."""
    def rule(d):
        b = fplib.get_or_else(cari_buku(state["buku"], d["buku_id"]), None)
        if b is None:
            return fplib.err(f"Buku {d['buku_id']} tidak ditemukan")
        return fplib.ok(d) if tersedia(b) else fplib.err(f"Buku {d['buku_id']} sedang dipinjam")
    return rule


def _cek_bentrok(state):
    """Rule: pencatatan mundur tidak boleh beririsan dengan periode pinjam nyata buku yang sama."""
    def rule(d):
        selesai = d["tgl_pinjam"] + timedelta(days=d["lama_hari"])
        bentrok = fplib.where(state["peminjaman"], fplib.and_(
            lambda p: p["buku_id"] == d["buku_id"],
            lambda p: fplib.is_overlap(p["tgl_pinjam"], p["tgl_kembali"] or p["tgl_jatuh_tempo"],
                                       d["tgl_pinjam"], selesai)))
        return fplib.err(f"Periode bentrok dengan peminjaman {bentrok[0]['id']}") if bentrok else fplib.ok(d)
    return rule


def _buat_peminjaman(state, d) -> tuple:
    """Buat record peminjaman; status buku diubah menjadi 'dipinjam'."""
    rec = {"id": f"P{len(state['peminjaman']) + 1:03d}", "anggota_id": d["anggota_id"],
           "buku_id": d["buku_id"], "tgl_pinjam": d["tgl_pinjam"],
           "tgl_jatuh_tempo": d["tgl_pinjam"] + timedelta(days=d["lama_hari"]), "tgl_kembali": None}
    buku_baru = fplib.update_where(
        state["buku"], lambda b: b["id"] == d["buku_id"],
        lambda b: fplib.assoc(fplib.assoc(b, "status", "dipinjam"), "jumlah_pinjam", b["jumlah_pinjam"] + 1))
    return ({**state, "buku": buku_baru, "peminjaman": state["peminjaman"] + (rec,)}, rec)


def pinjam(state: Dict[str, Any], d: Dict[str, Any]):
    """Proses peminjaman -> ok((state_baru, record)) atau err(pesan)."""
    return fplib.pipe(
        d,
        validasi_peminjaman,
        lambda r: fplib.flat_map(r, _cek_anggota(state)),
        lambda r: fplib.flat_map(r, _cek_tersedia(state)),
        lambda r: fplib.flat_map(r, _cek_bentrok(state)),
        lambda r: fplib.map_result(r, lambda x: _buat_peminjaman(state, x)),
    )


def hitung_denda(tgl_jatuh_tempo: date, tgl_kembali: date) -> int:
    """Denda = hari terlambat x tarif per hari (0 jika tepat waktu)."""
    return max(0, fplib.diff_days(tgl_jatuh_tempo, tgl_kembali)) * data.DENDA_PER_HARI


def kembalikan(state: Dict[str, Any], peminjaman_id: str, tgl_kembali: date):
    """Proses pengembalian -> ok((state_baru, info)); info['tagihan'] adalah Option tagihan denda."""
    p = fplib.get_or_else(cari_peminjaman(state["peminjaman"], peminjaman_id), None)
    if p is None or p["tgl_kembali"] is not None:
        return fplib.err(f"Peminjaman {peminjaman_id} tidak ditemukan atau sudah dikembalikan")
    telat = max(0, fplib.diff_days(p["tgl_jatuh_tempo"], tgl_kembali))
    denda = hitung_denda(p["tgl_jatuh_tempo"], tgl_kembali)
    tagihan = fplib.some({
        "id": f"TGH-{p['id']}-D", "jenis": "denda", "anggota_id": p["anggota_id"], "jumlah": denda,
        "tanggal": tgl_kembali, "lunas": False,
        "keterangan": f"Denda telat {telat} hari ({p['buku_id']}) = {fplib.format_rupiah(denda)}",
    }) if denda > 0 else fplib.none()
    state_baru = {
        **state,
        "peminjaman": fplib.update_where(state["peminjaman"], lambda x: x["id"] == peminjaman_id,
                                         lambda x: fplib.assoc(x, "tgl_kembali", tgl_kembali)),
        "buku": fplib.update_where(state["buku"], lambda b: b["id"] == p["buku_id"],
                                   lambda b: fplib.assoc(b, "status", "tersedia")),
    }
    return fplib.ok((state_baru, {"hari_telat": telat, "denda": denda, "tagihan": tagihan}))


def _judul(daftar) -> tuple:
    """Ambil judul dari daftar buku."""
    return tuple(map(lambda b: b["judul"], daftar))


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 1: PERPUSTAKAAN\n", "=" * 50, sep="")
    s0 = {"buku": data.BUKU, "anggota": data.ANGGOTA, "peminjaman": ()}
    print("Jumlah buku per kategori :", jumlah_buku_per_kategori(data.BUKU))
    print("Novel yang tersedia      :", _judul(buku_tersedia_kategori(data.BUKU, "Novel")))
    print("2 buku terpopuler        :", _judul(buku_terpopuler(data.BUKU, 2)))
    print("Cari buku B999 (Option)  :", fplib.get_or_else(cari_buku(data.BUKU, "B999"), "tidak ditemukan"))

    print("\n[BERHASIL] Andi meminjam B001 pada 2026-11-01 (7 hari)")
    _, (s1, p1) = pinjam(s0, {"anggota_id": "A001", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 1), "lama_hari": 7})
    print("  Jatuh tempo:", p1["tgl_jatuh_tempo"], "| sedang dipinjam:", _judul(buku_dipinjam(s1["buku"])))

    print("\n[GAGAL] Citra meminjam B001 yang sedang dipinjam")
    print(" ", pinjam(s1, {"anggota_id": "A003", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 3), "lama_hari": 7}))
    print("[GAGAL] Data tidak valid (lama_hari = 30)")
    print(" ", pinjam(s1, {"anggota_id": "A003", "buku_id": "B002", "tgl_pinjam": date(2026, 11, 3), "lama_hari": 30}))

    print("\n[BERHASIL] Andi mengembalikan 2026-11-11 (telat)")
    _, (s2, info) = kembalikan(s1, p1["id"], date(2026, 11, 11))
    print(f"  Telat {info['hari_telat']} hari, denda {fplib.format_rupiah(info['denda'])}")
    print("[GAGAL] Pencatatan mundur Citra 2026-11-03 beririsan dengan periode Andi")
    print(" ", pinjam(s2, {"anggota_id": "A003", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 3), "lama_hari": 7}))
