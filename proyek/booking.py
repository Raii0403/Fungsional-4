"""booking.py - Aplikasi 2: sewa ruang diskusi per jam.

State: {"ruangan", "booking"}. Setiap operasi mengembalikan state BARU.
Jalankan sendiri: python booking.py
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Dict

import data
import fplib

validasi_booking = fplib.validate(
    fplib.required("anggota_id"), fplib.min_length("anggota_id", 4),
    fplib.required("ruangan_id"), fplib.required("tanggal"),
    fplib.in_range("jam_mulai", 8, 18), fplib.in_range("durasi", 1, 4),
    fplib.in_range("peserta", 1, 20),
)


def cari_ruangan(daftar, ruangan_id: str):
    """Cari ruangan berdasarkan ID; Option."""
    hasil = fplib.where(daftar, lambda r: r["id"] == ruangan_id)
    return fplib.some(hasil[0]) if hasil else fplib.none()


def _waktu(d) -> tuple:
    """Hitung (mulai, selesai) sebagai datetime."""
    mulai = datetime.combine(d["tanggal"], time(d["jam_mulai"]))
    return (mulai, mulai + timedelta(hours=d["durasi"]))


# ------------------------------------------------------------ predikat ruangan
def kapasitas_cukup(peserta: int):
    """Pabrik predikat: kapasitas ruangan >= peserta."""
    return lambda r: r["kapasitas"] >= peserta


def kosong(state, mulai: datetime, selesai: datetime):
    """Pabrik predikat: ruangan tidak punya booking beririsan pada rentang waktu."""
    return lambda r: not fplib.where(state["booking"], fplib.and_(
        lambda b: b["ruangan_id"] == r["id"],
        lambda b: fplib.is_overlap(b["mulai"], b["selesai"], mulai, selesai)))


def ruangan_tersedia(state, mulai: datetime, selesai: datetime, peserta: int) -> tuple:
    """Ruangan yang kosong pada rentang waktu DAN kapasitasnya cukup."""
    return fplib.where(state["ruangan"], fplib.and_(kapasitas_cukup(peserta), kosong(state, mulai, selesai)))


# ------------------------------------------------------------------- rule
def _cek_tanggal(hari_ini: date):
    """Rule: tanggal booking tidak boleh sebelum hari ini."""
    return lambda d: (fplib.ok(d) if fplib.diff_days(hari_ini, d["tanggal"]) >= 0
                      else fplib.err("Tanggal booking sudah lewat"))


def _cek_denda(tagihan):
    """Rule: tolak anggota yang masih punya denda belum lunas."""
    def rule(d):
        belum = fplib.where(tagihan, fplib.and_(
            lambda t: t["jenis"] == "denda", fplib.not_(lambda t: t["lunas"]),
            lambda t: t["anggota_id"] == d["anggota_id"]))
        total = fplib.sum_by(belum, lambda t: t["jumlah"])
        return fplib.err(f"Masih ada denda {fplib.format_rupiah(total)}") if total > 0 else fplib.ok(d)
    return rule


def _cek_ruangan(state):
    """Rule: ruangan harus ada, kapasitas cukup; sisipkan data ruangan."""
    def rule(d):
        r = fplib.get_or_else(cari_ruangan(state["ruangan"], d["ruangan_id"]), None)
        if r is None:
            return fplib.err(f"Ruangan {d['ruangan_id']} tidak ditemukan")
        if not kapasitas_cukup(d["peserta"])(r):
            return fplib.err(f"Kapasitas {r['nama']} hanya {r['kapasitas']} orang")
        return fplib.ok({**d, "ruangan": r})
    return rule


def _cek_bentrok(state):
    """Rule: jam tidak boleh beririsan dengan booking lain di ruangan yang sama."""
    def rule(d):
        mulai, selesai = _waktu(d)
        bentrok = fplib.where(state["booking"], fplib.and_(
            lambda b: b["ruangan_id"] == d["ruangan_id"],
            lambda b: fplib.is_overlap(b["mulai"], b["selesai"], mulai, selesai)))
        return fplib.err(f"Jadwal bentrok dengan booking {bentrok[0]['id']}") if bentrok else fplib.ok(d)
    return rule


# ----------------------------------------------------------------- proses
def konfirmasi(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Salinan booking dengan status 'dikonfirmasi'."""
    return fplib.assoc(rec, "status", "dikonfirmasi")


def konfirmasi_booking(state, booking_id: str) -> Dict[str, Any]:
    """State baru dengan satu booking dikonfirmasi."""
    return {**state, "booking": fplib.update_where(state["booking"], lambda b: b["id"] == booking_id, konfirmasi)}


def _simpan(state, d) -> tuple:
    """Simpan booking berstatus 'menunggu' -> (state_baru, record)."""
    mulai, selesai = _waktu(d)
    rec = {"id": f"BK{len(state['booking']) + 1:03d}", "anggota_id": d["anggota_id"],
           "ruangan_id": d["ruangan_id"], "status": "menunggu", "mulai": mulai, "selesai": selesai,
           "biaya": d["ruangan"]["tarif_per_jam"] * d["durasi"]}
    return ({**state, "booking": state["booking"] + (rec,)}, rec)


def pesan_ruangan(state: Dict[str, Any], d: Dict[str, Any], tagihan, hari_ini: date):
    """Proses booking -> ok((state_baru, record dikonfirmasi)) atau err(pesan)."""
    return fplib.pipe(
        d,
        validasi_booking,
        lambda r: fplib.flat_map(r, _cek_tanggal(hari_ini)),
        lambda r: fplib.flat_map(r, _cek_denda(tagihan)),
        lambda r: fplib.flat_map(r, _cek_ruangan(state)),
        lambda r: fplib.flat_map(r, _cek_bentrok(state)),
        lambda r: fplib.map_result(r, lambda x: _simpan(state, x)),
        lambda r: fplib.map_result(r, lambda sr: (konfirmasi_booking(sr[0], sr[1]["id"]), konfirmasi(sr[1]))),
    )


# compose: ambil daftar booking, kelompokkan per ruangan, lalu jumlahkan biayanya
pendapatan_per_ruangan = fplib.compose(
    lambda grup: {rid: fplib.sum_by(items, lambda b: b["biaya"]) for rid, items in grup.items()},
    lambda daftar: fplib.group_by(daftar, lambda b: b["ruangan_id"]),
    lambda state: state["booking"],
)


def ruangan_terlaris(state, n: int) -> tuple:
    """n ruangan dengan pendapatan terbesar -> tuple (id, pendapatan)."""
    return fplib.top_n(tuple(pendapatan_per_ruangan(state).items()), lambda kv: kv[1], n)


def jadwal_urut(state) -> tuple:
    """Booking terurut menurut waktu mulai."""
    return fplib.sort_by(state["booking"], lambda b: b["mulai"])


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 2: BOOKING RUANGAN\n", "=" * 50, sep="")
    hari_ini = date(2026, 11, 11)
    s0 = {"ruangan": data.RUANGAN, "booking": data.BOOKING_AWAL}
    mulai, selesai = datetime(2026, 11, 12, 9), datetime(2026, 11, 12, 11)
    print("Ruangan kosong 12 Nov 09-11 untuk 8 orang:",
          tuple(map(lambda r: r["nama"], ruangan_tersedia(s0, mulai, selesai, 8))))
    print("Cari ruangan R99 (Option):", fplib.get_or_else(cari_ruangan(data.RUANGAN, "R99"), "tidak ditemukan"))

    print("\n[GAGAL] Budi (punya denda) memesan R01")
    print(" ", pesan_ruangan(s0, {"anggota_id": "A002", "ruangan_id": "R01", "tanggal": date(2026, 11, 13),
                                  "jam_mulai": 10, "durasi": 2, "peserta": 4}, data.TAGIHAN_AWAL, hari_ini))
    print("[GAGAL] Citra memesan R01 jam 10 (bentrok dengan BK001)")
    print(" ", pesan_ruangan(s0, {"anggota_id": "A003", "ruangan_id": "R01", "tanggal": date(2026, 11, 12),
                                  "jam_mulai": 10, "durasi": 2, "peserta": 4}, data.TAGIHAN_AWAL, hari_ini))
    print("[BERHASIL] Citra memesan R01 jam 13 selama 2 jam")
    _, (s1, bk) = pesan_ruangan(s0, {"anggota_id": "A003", "ruangan_id": "R01", "tanggal": date(2026, 11, 12),
                                     "jam_mulai": 13, "durasi": 2, "peserta": 4}, data.TAGIHAN_AWAL, hari_ini)
    print(f"  {bk['id']} status {bk['status']}, biaya {fplib.format_rupiah(bk['biaya'])}")
    print("\nJadwal terurut :", tuple(map(lambda b: (b["id"], f"{b['mulai']:%d/%m %H:%M}"), jadwal_urut(s1))))
    print("Pendapatan     :", {k: fplib.format_rupiah(v) for k, v in pendapatan_per_ruangan(s1).items()})
    print("Ruangan terlaris:", tuple(map(lambda kv: (kv[0], fplib.format_rupiah(kv[1])), ruangan_terlaris(s1, 1))))
