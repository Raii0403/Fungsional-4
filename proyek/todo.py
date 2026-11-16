"""todo.py - Aplikasi 5: tugas staf (sebagian dibuat otomatis oleh sistem lain).

State: tuple tugas (immutable).
"""
from datetime import date, timedelta
from typing import Any, Dict

from data import PRIORITAS
from fplib import (Result, compose, diff_days, err, flat_map, get_or_else,
                   group_by, is_overlap, map_result, min_length, none, ok,
                   pipe, required, some, sum_by, validate)


def _prioritas_valid(data) -> Result:
    """Rule: prioritas harus tinggi/sedang/rendah."""
    return ok(data) if data.get("prioritas") in PRIORITAS else err("Prioritas harus tinggi, sedang, atau rendah")


def _deadline_valid(hari_ini: date):
    """Rule: deadline tidak boleh sebelum hari ini."""
    return lambda d: ok(d) if diff_days(hari_ini, d["deadline"]) >= 0 else err("Deadline sudah lewat")


def _cek_duplikat(daftar: tuple):
    """Rule: tolak tugas aktif dengan judul yang sama."""
    return lambda d: (
        err(f"Tugas '{d['judul']}' sudah ada")
        if any(map(lambda t: t["judul"] == d["judul"] and not t["selesai"], daftar))
        else ok(d))


def cari_tugas(daftar: tuple, tugas_id: str):
    """Cari tugas berdasarkan ID; Option."""
    return next((some(t) for t in daftar if t["id"] == tugas_id), none())


def sisa_hari(tugas: Dict[str, Any], hari_ini: date) -> int:
    """Sisa hari menuju deadline."""
    return diff_days(hari_ini, tugas["deadline"])


def _simpan(daftar, d, hari_ini) -> tuple:
    """Bentuk record tugas dan tuple baru."""
    rec = {"id": f"T{len(daftar) + 1:03d}", "judul": d["judul"], "prioritas": d["prioritas"],
           "mulai": hari_ini, "deadline": d["deadline"],
           "otomatis": d.get("otomatis", False), "selesai": False}
    return (daftar + (rec,), rec)


def buat_tugas(daftar: tuple, data: Dict[str, Any], hari_ini: date) -> Result:
    """Tambah tugas -> ok((daftar_baru, tugas)) atau err(pesan)."""
    return pipe(
        data,
        validate(required("judul"), min_length("judul", 5), required("deadline"),
                 _deadline_valid(hari_ini), _prioritas_valid),
        lambda r: flat_map(r, _cek_duplikat(daftar)),
        lambda r: map_result(r, lambda d: _simpan(daftar, d, hari_ini)),
    )


def buat_tugas_otomatis(daftar: tuple, judul: str, hari_ini: date, prioritas: str = "tinggi") -> Result:
    """Tugas otomatis dari sistem lain; deadline besok."""
    return buat_tugas(daftar, {"judul": judul, "prioritas": prioritas,
                               "deadline": hari_ini + timedelta(days=1), "otomatis": True}, hari_ini)


def selesaikan(daftar: tuple, tugas_id: str) -> Result:
    """Tandai tugas selesai -> ok(daftar_baru) atau err(pesan)."""
    t = get_or_else(cari_tugas(daftar, tugas_id), None)
    return err(f"Tugas {tugas_id} tidak ditemukan") if t is None else ok(
        tuple(map(lambda x: {**x, "selesai": True} if x["id"] == tugas_id else x, daftar)))


def tugas_bentrok(daftar: tuple, tugas: Dict[str, Any]) -> tuple:
    """Tugas aktif lain yang periodenya beririsan dengan tugas ini."""
    return tuple(filter(
        lambda t: not t["selesai"] and t["id"] != tugas["id"]
        and is_overlap(t["mulai"], t["deadline"], tugas["mulai"], tugas["deadline"]),
        daftar))


def per_prioritas(daftar: tuple) -> Dict[str, tuple]:
    """Kelompokkan tugas per prioritas."""
    return group_by(daftar, lambda t: t["prioritas"])


# compose: kelompokkan per prioritas, lalu hitung jumlah tugas tiap prioritas
jumlah_per_prioritas = compose(
    lambda grup: {p: sum_by(v, lambda _: 1) for p, v in grup.items()},
    per_prioritas,
)


def laporan(daftar: tuple, hari_ini: date) -> str:
    """Hasilkan teks daftar tugas per prioritas."""
    grup = per_prioritas(daftar)
    baris = lambda t: (f"    [{'x' if t['selesai'] else ' '}] {t['id']} {t['judul']} "
                       f"(deadline {t['deadline']}, sisa {sisa_hari(t, hari_ini)} hari)"
                       + (" [otomatis]" if t["otomatis"] else ""))
    bagian = lambda p: (f"  Prioritas {p.upper()}:",) + tuple(map(baris, grup.get(p, ())))
    return "\n".join(sum(map(bagian, filter(lambda p: p in grup, PRIORITAS)), ()))
