"""booking.py - Aplikasi 2: sewa ruang diskusi per jam.

State: {"ruangan", "booking"}. Operasi mengembalikan state baru.
"""
from datetime import date, datetime, time, timedelta
from typing import Any, Dict

from fplib import (Result, compose, diff_days, err, flat_map, format_rupiah, get_or_else,
                   group_by, in_range, is_overlap, map_result, min_length, none, ok, pipe,
                   required, some, sum_by, validate)

validasi_booking = validate(
    required("anggota_id"), min_length("anggota_id", 4), required("ruangan_id"), required("tanggal"),
    in_range("jam_mulai", 8, 18), in_range("durasi", 1, 4),
)


def cari_ruangan(daftar, ruangan_id: str):
    """Cari ruangan berdasarkan ID; Option."""
    return next((some(r) for r in daftar if r["id"] == ruangan_id), none())


def _waktu(data) -> tuple:
    """Hitung (mulai, selesai) sebagai datetime dari data booking."""
    mulai = datetime.combine(data["tanggal"], time(data["jam_mulai"]))
    return (mulai, mulai + timedelta(hours=data["durasi"]))


def _cek_tanggal(hari_ini: date):
    """Rule: tanggal booking tidak boleh sebelum hari ini."""
    return lambda d: ok(d) if diff_days(hari_ini, d["tanggal"]) >= 0 else err("Tanggal booking sudah lewat")


def _cek_denda(tagihan):
    """Rule: tolak anggota yang masih punya denda belum lunas."""
    def rule(d) -> Result:
        belum = tuple(filter(
            lambda t: t["jenis"] == "denda" and not t["lunas"] and t["anggota_id"] == d["anggota_id"],
            tagihan))
        total = sum_by(belum, lambda t: t["jumlah"])
        return err(f"Masih ada denda {format_rupiah(total)}") if total > 0 else ok(d)
    return rule


def _cek_ruangan(state):
    """Rule: ruangan harus ada; sisipkan data ruangan ke hasil."""
    def rule(d) -> Result:
        r = get_or_else(cari_ruangan(state["ruangan"], d["ruangan_id"]), None)
        return ok({**d, "ruangan": r}) if r else err(f"Ruangan {d['ruangan_id']} tidak ditemukan")
    return rule


def _cek_bentrok(state):
    """Rule: jam tidak boleh beririsan dengan booking lain di ruangan yang sama."""
    def rule(d) -> Result:
        mulai, selesai = _waktu(d)
        bentrok = tuple(filter(
            lambda b: b["ruangan_id"] == d["ruangan_id"]
            and is_overlap(b["mulai"], b["selesai"], mulai, selesai),
            state["booking"]))
        return err(f"Jadwal bentrok dengan booking {bentrok[0]['id']}") if bentrok else ok(d)
    return rule


def _buat_booking(state, d) -> tuple:
    """Bentuk record booking dan state baru."""
    mulai, selesai = _waktu(d)
    rec = {"id": f"B{len(state['booking']) + 1:03d}", "anggota_id": d["anggota_id"],
           "ruangan_id": d["ruangan_id"], "mulai": mulai, "selesai": selesai,
           "biaya": d["ruangan"]["tarif_per_jam"] * d["durasi"]}
    return ({**state, "booking": state["booking"] + (rec,)}, rec)


def pesan_ruangan(state: Dict[str, Any], data: Dict[str, Any], tagihan, hari_ini: date) -> Result:
    """Proses booking -> ok((state_baru, record)) atau err(pesan)."""
    return pipe(
        data,
        validasi_booking,
        lambda r: flat_map(r, _cek_tanggal(hari_ini)),
        lambda r: flat_map(r, _cek_denda(tagihan)),
        lambda r: flat_map(r, _cek_ruangan(state)),
        lambda r: flat_map(r, _cek_bentrok(state)),
        lambda r: map_result(r, lambda d: _buat_booking(state, d)),
    )


# compose: ambil daftar booking, kelompokkan per ruangan, lalu jumlahkan biayanya
pendapatan_per_ruangan = compose(
    lambda grup: {rid: sum_by(items, lambda b: b["biaya"]) for rid, items in grup.items()},
    lambda daftar: group_by(daftar, lambda b: b["ruangan_id"]),
    lambda state: state["booking"],
)
