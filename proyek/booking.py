"""booking.py - Aplikasi 2: sewa ruang diskusi per jam.

Hasil operasi berupa tuple (True, data) atau (False, "pesan error").
State: {"ruangan", "booking"}; setiap operasi mengembalikan state BARU.
Jalankan sendiri: python booking.py
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Dict

import data
import fplib

MAKS_HARI_DI_MUKA = 7

ATURAN_BOOKING = [
    (lambda d: d.get("anggota_id", "") != "", "ID anggota wajib diisi"),
    (lambda d: d.get("ruangan_id", "") != "", "ID ruangan wajib diisi"),
    (lambda d: d.get("tanggal") is not None, "Tanggal wajib diisi"),
    (lambda d: d.get("jam_mulai", 0) >= 8, "Jam mulai paling awal 08:00"),
    (lambda d: 1 <= d.get("durasi", 0) <= 4, "Durasi harus 1-4 jam"),
    (lambda d: d.get("jam_mulai", 0) + d.get("durasi", 0) <= 21, "Booking harus selesai paling lambat 21:00"),
]


def cari_ruangan(daftar, ruangan_id: str):
    """Cari ruangan berdasarkan ID; None jika tidak ada."""
    return fplib.find_by(daftar, lambda r: r["id"] == ruangan_id)


def denda_belum_lunas(tagihan, anggota_id: str) -> int:
    """Total denda anggota yang belum dibayar."""
    belum = fplib.where(tagihan, lambda t: t["jenis"] == "denda", lambda t: t["anggota_id"] == anggota_id,
                        lambda t: not t["lunas"])
    return fplib.sum_by(belum, lambda t: t["jumlah"])


def booking_bentrok(daftar, ruangan_id: str, mulai: datetime, selesai: datetime) -> tuple:
    """Booking di ruangan yang sama yang jamnya bertabrakan dengan [mulai, selesai)."""
    return fplib.where(daftar, lambda b: b["ruangan_id"] == ruangan_id,
                       lambda b: mulai < b["selesai"] and b["mulai"] < selesai)


def pesan_ruangan(state: Dict[str, Any], d: Dict[str, Any], tagihan, hari_ini: date):
    """Proses booking -> (True, (state_baru, record)) atau (False, pesan)."""
    galat = fplib.validate(d, ATURAN_BOOKING)
    if galat:
        return (False, "; ".join(galat))
    if not 0 <= fplib.diff_days(hari_ini, d["tanggal"]) <= MAKS_HARI_DI_MUKA:
        return (False, f"Booking hanya bisa untuk 0-{MAKS_HARI_DI_MUKA} hari ke depan")
    denda = denda_belum_lunas(tagihan, d["anggota_id"])
    if denda > 0:
        return (False, f"Masih ada denda {fplib.format_rupiah(denda)}")
    ruangan = cari_ruangan(state["ruangan"], d["ruangan_id"])
    if ruangan is None:
        return (False, f"Ruangan {d['ruangan_id']} tidak ditemukan")
    mulai = datetime.combine(d["tanggal"], time(d["jam_mulai"]))
    selesai = mulai + timedelta(hours=d["durasi"])
    bentrok = booking_bentrok(state["booking"], ruangan["id"], mulai, selesai)
    if bentrok:
        return (False, f"Jadwal bentrok dengan booking {bentrok[0]['id']}")
    bk_id = f"BK{len(state['booking']) + 1:03d}"
    rec = {"id": bk_id, "anggota_id": d["anggota_id"], "ruangan_id": ruangan["id"], "status": "menunggu",
           "mulai": mulai, "selesai": selesai,
           "biaya": fplib.pipe(d["durasi"], lambda jam: jam * ruangan["tarif_per_jam"])}
    sementara = state["booking"] + (rec,)
    state_baru = {**state, "booking": fplib.update_where(sementara, lambda b: b["id"] == bk_id,
                                                         {"status": "dikonfirmasi"})}
    return (True, (state_baru, fplib.find_by(state_baru["booking"], lambda b: b["id"] == bk_id)))


def jadwal_urut(state) -> tuple:
    """Booking terurut menurut waktu mulai."""
    return fplib.sort_by(state["booking"], lambda b: b["mulai"])


def pendapatan_per_ruangan(state) -> Dict[str, int]:
    """Total biaya sewa per ruangan."""
    grup = fplib.group_by(state["booking"], lambda b: b["ruangan_id"])
    return {rid: fplib.sum_by(items, lambda b: b["biaya"]) for rid, items in grup.items()}


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 2: BOOKING RUANGAN\n", "=" * 50, sep="")
    hari_ini = date(2026, 11, 11)
    s0 = {"ruangan": data.RUANGAN, "booking": data.BOOKING_AWAL}
    base = {"anggota_id": "A003", "ruangan_id": "R01", "tanggal": date(2026, 11, 12), "jam_mulai": 13, "durasi": 2}
    print("Cari ruangan R99 :", cari_ruangan(data.RUANGAN, "R99"))
    print("\n[GAGAL] Budi (punya denda) memesan     :", pesan_ruangan(s0, {**base, "anggota_id": "A002"}, data.TAGIHAN_AWAL, hari_ini))
    print("[GAGAL] Citra jam 10 (bentrok BK001)   :", pesan_ruangan(s0, {**base, "jam_mulai": 10}, data.TAGIHAN_AWAL, hari_ini))
    print("[GAGAL] Tanggal terlalu jauh (H+14)    :", pesan_ruangan(s0, {**base, "tanggal": date(2026, 11, 25)}, data.TAGIHAN_AWAL, hari_ini))
    print("[GAGAL] Jam di luar operasional        :", pesan_ruangan(s0, {**base, "jam_mulai": 20, "durasi": 3}, data.TAGIHAN_AWAL, hari_ini))
    print("[BERHASIL] Citra memesan R01 jam 13-15")
    _, (s1, bk) = pesan_ruangan(s0, base, data.TAGIHAN_AWAL, hari_ini)
    print(f"  {bk['id']} status {bk['status']}, biaya {fplib.format_rupiah(bk['biaya'])}")
    print("\nJadwal terurut :", tuple(map(lambda b: (b["id"], f"{b['mulai']:%d/%m %H:%M}"), jadwal_urut(s1))))
    print("Pendapatan     :", {k: fplib.format_rupiah(v) for k, v in pendapatan_per_ruangan(s1).items()})
