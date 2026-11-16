"""perpustakaan.py - Aplikasi 1: peminjaman buku dan perhitungan denda.

State berbentuk dict {"buku", "anggota", "peminjaman"}; setiap operasi
mengembalikan state BARU (state lama tidak diubah).
"""
from datetime import date, timedelta
from typing import Any, Dict

from data import DENDA_PER_HARI
from fplib import (Result, compose, diff_days, err, flat_map, format_rupiah,
                   get_or_else, group_by, in_range, is_overlap, map_result,
                   min_length, none, ok, pipe, required, some, sum_by, validate)

validasi_peminjaman = validate(
    required("anggota_id"), min_length("anggota_id", 4), required("buku_id"),
    required("tgl_pinjam"), in_range("lama_hari", 1, 14),
)


def cari_buku(daftar, buku_id: str):
    """Cari buku berdasarkan ID; Option karena buku mungkin tidak ada."""
    return next((some(b) for b in daftar if b["id"] == buku_id), none())


def cari_anggota(daftar, anggota_id: str):
    """Cari anggota berdasarkan ID; Option."""
    return next((some(a) for a in daftar if a["id"] == anggota_id), none())


def cari_peminjaman(daftar, peminjaman_id: str):
    """Cari peminjaman berdasarkan ID; Option."""
    return next((some(p) for p in daftar if p["id"] == peminjaman_id), none())


def buku_per_kategori(daftar) -> Dict[str, tuple]:
    """Kelompokkan buku per kategori."""
    return group_by(daftar, lambda b: b["kategori"])


# compose: kelompokkan per kategori, lalu hitung jumlah buku tiap kategori
jumlah_buku_per_kategori = compose(
    lambda grup: {k: sum_by(v, lambda _: 1) for k, v in grup.items()},
    buku_per_kategori,
)


def _cek_anggota(state):
    """Rule: anggota harus terdaftar."""
    def rule(data) -> Result:
        a = get_or_else(cari_anggota(state["anggota"], data["anggota_id"]), None)
        return ok(data) if a else err(f"Anggota {data['anggota_id']} tidak ditemukan")
    return rule


def _cek_buku(state):
    """Rule: buku harus ada di katalog."""
    def rule(data) -> Result:
        b = get_or_else(cari_buku(state["buku"], data["buku_id"]), None)
        return ok(data) if b else err(f"Buku {data['buku_id']} tidak ditemukan")
    return rule


def _cek_bentrok(state):
    """Rule: buku yang sama tidak boleh dipinjam pada periode yang beririsan."""
    def rule(data) -> Result:
        selesai = data["tgl_pinjam"] + timedelta(days=data["lama_hari"])
        bentrok = tuple(filter(
            lambda p: p["buku_id"] == data["buku_id"] and p["tgl_kembali"] is None
            and is_overlap(p["tgl_pinjam"], p["tgl_jatuh_tempo"], data["tgl_pinjam"], selesai),
            state["peminjaman"]))
        return err(f"Buku {data['buku_id']} sedang dipinjam pada periode tersebut") if bentrok else ok(data)
    return rule


def _buat_peminjaman(state, data) -> tuple:
    """Bentuk record peminjaman dan state baru."""
    rec = {
        "id": f"P{len(state['peminjaman']) + 1:03d}",
        "anggota_id": data["anggota_id"], "buku_id": data["buku_id"],
        "tgl_pinjam": data["tgl_pinjam"],
        "tgl_jatuh_tempo": data["tgl_pinjam"] + timedelta(days=data["lama_hari"]),
        "tgl_kembali": None,
    }
    return ({**state, "peminjaman": state["peminjaman"] + (rec,)}, rec)


def pinjam(state: Dict[str, Any], data: Dict[str, Any]) -> Result:
    """Proses peminjaman -> ok((state_baru, record)) atau err(pesan)."""
    return pipe(
        data,
        validasi_peminjaman,
        lambda r: flat_map(r, _cek_anggota(state)),
        lambda r: flat_map(r, _cek_buku(state)),
        lambda r: flat_map(r, _cek_bentrok(state)),
        lambda r: map_result(r, lambda d: _buat_peminjaman(state, d)),
    )


def hitung_denda(tgl_jatuh_tempo: date, tgl_kembali: date) -> int:
    """Denda = hari terlambat x tarif per hari (0 jika tepat waktu)."""
    return max(0, diff_days(tgl_jatuh_tempo, tgl_kembali)) * DENDA_PER_HARI


def kembalikan(state: Dict[str, Any], peminjaman_id: str, tgl_kembali: date) -> Result:
    """Proses pengembalian -> ok((state_baru, info)); info['tagihan'] berupa Option tagihan denda."""
    p = get_or_else(cari_peminjaman(state["peminjaman"], peminjaman_id), None)
    if p is None or p["tgl_kembali"] is not None:
        return err(f"Peminjaman {peminjaman_id} tidak ditemukan atau sudah dikembalikan")
    telat = max(0, diff_days(p["tgl_jatuh_tempo"], tgl_kembali))
    denda = hitung_denda(p["tgl_jatuh_tempo"], tgl_kembali)
    tagihan = some({
        "id": f"TGH-{p['id']}-D", "jenis": "denda", "anggota_id": p["anggota_id"],
        "jumlah": denda, "tanggal": tgl_kembali, "lunas": False,
        "keterangan": f"Denda telat {telat} hari ({p['buku_id']}) = {format_rupiah(denda)}",
    }) if denda > 0 else none()
    baru = tuple(map(lambda x: {**x, "tgl_kembali": tgl_kembali} if x["id"] == peminjaman_id else x,
                     state["peminjaman"]))
    return ok(({**state, "peminjaman": baru},
               {"hari_telat": telat, "denda": denda, "tagihan": tagihan}))
