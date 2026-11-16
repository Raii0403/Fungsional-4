"""todo.py - Aplikasi 5: tugas staf (sebagian dibuat otomatis oleh sistem lain).

Hasil operasi berupa tuple (True, data) atau (False, "pesan error").
State: tuple tugas (immutable); setiap operasi mengembalikan tuple BARU.
Jalankan sendiri: python todo.py
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

import data
import fplib


def cari_tugas(daftar: tuple, tugas_id: str):
    """Cari tugas berdasarkan ID; None jika tidak ada."""
    return fplib.find_by(daftar, lambda t: t["id"] == tugas_id)


def sisa_hari(tugas: Dict[str, Any], hari_ini: date) -> int:
    """Sisa hari menuju deadline."""
    return fplib.diff_days(hari_ini, tugas["deadline"])


def buat_tugas(daftar: tuple, d: Dict[str, Any], hari_ini: date):
    """Tambah tugas -> (True, (daftar_baru, tugas)) atau (False, pesan)."""
    aturan = [
        (lambda x: len(x.get("judul", "")) >= 5, "Judul minimal 5 karakter"),
        (lambda x: x.get("deadline") is not None, "Deadline wajib diisi"),
        (lambda x: x.get("deadline") is None or fplib.diff_days(hari_ini, x["deadline"]) >= 0, "Deadline sudah lewat"),
        (lambda x: x.get("prioritas") in data.PRIORITAS, "Prioritas harus tinggi, sedang, atau rendah"),
        (lambda x: 1 <= x.get("estimasi_jam", 0) <= 40, "Estimasi harus 1-40 jam"),
    ]
    galat = fplib.validate(d, aturan)
    if galat:
        return (False, "; ".join(galat))
    rec = {"id": f"T{len(daftar) + 1:03d}", "judul": d["judul"], "prioritas": d["prioritas"],
           "estimasi_jam": d["estimasi_jam"], "deadline": d["deadline"],
           "otomatis": d.get("otomatis", False), "selesai": False}
    return (True, (daftar + (rec,), rec))


def buat_tugas_otomatis(daftar: tuple, judul: str, hari_ini: date):
    """Tugas otomatis dari sistem lain: prioritas tinggi, deadline besok."""
    return buat_tugas(daftar, {"judul": judul, "prioritas": "tinggi", "estimasi_jam": 1,
                               "deadline": hari_ini + timedelta(days=1), "otomatis": True}, hari_ini)


def tandai_selesai(daftar: tuple, tugas_id: str):
    """Tandai tugas selesai -> (True, daftar_baru) atau (False, pesan)."""
    if cari_tugas(daftar, tugas_id) is None:
        return (False, f"Tugas {tugas_id} tidak ditemukan")
    return (True, fplib.update_where(daftar, lambda t: t["id"] == tugas_id, {"selesai": True}))


def tugas_mendesak(daftar: tuple) -> tuple:
    """Tugas belum selesai DAN prioritas tinggi, urut deadline terdekat."""
    return fplib.sort_by(fplib.where(daftar, lambda t: not t["selesai"], lambda t: t["prioritas"] == "tinggi"),
                         lambda t: t["deadline"])


def jam_per_prioritas(daftar: tuple) -> Dict[str, int]:
    """Total estimasi jam kerja tugas belum selesai per prioritas."""
    grup = fplib.group_by(fplib.where(daftar, lambda t: not t["selesai"]), lambda t: t["prioritas"])
    return {p: fplib.sum_by(v, lambda t: t["estimasi_jam"]) for p, v in grup.items()}


def laporan(daftar: tuple, hari_ini: date) -> str:
    """Alur pipe: saring belum selesai -> urut deadline -> kelompok prioritas -> teks."""
    baris = lambda t: (f"    {t['id']} {t['judul']} (deadline {t['deadline']}, sisa {sisa_hari(t, hari_ini)} hari, "
                       f"{t['estimasi_jam']} jam)" + (" [otomatis]" if t["otomatis"] else ""))
    teks = lambda grup: "\n".join(sum(tuple(
        (f"  Prioritas {p.upper()}:",) + tuple(map(baris, grup[p])) for p in data.PRIORITAS if p in grup), ()))
    return fplib.pipe(
        daftar,
        lambda d: fplib.where(d, lambda t: not t["selesai"]),
        lambda d: fplib.sort_by(d, lambda t: t["deadline"]),
        lambda d: fplib.group_by(d, lambda t: t["prioritas"]),
        teks,
    )


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 5: TODO STAF\n", "=" * 50, sep="")
    hari_ini = date(2026, 11, 11)
    s0 = data.TUGAS_AWAL
    print("[BERHASIL] Tugas manual")
    _, (s1, t) = buat_tugas(s0, {"judul": "Siapkan laporan bulanan", "prioritas": "tinggi",
                                 "estimasi_jam": 3, "deadline": date(2026, 11, 14)}, hari_ini)
    print(f"  {t['id']} {t['judul']} (sisa {sisa_hari(t, hari_ini)} hari)")
    print("[BERHASIL] Tugas otomatis dari sistem lain")
    _, (s2, t2) = buat_tugas_otomatis(s1, "Buka blokir anggota Andi", hari_ini)
    print(f"  {t2['id']} {t2['judul']} [otomatis={t2['otomatis']}]")
    print("[GAGAL] Judul pendek      :", buat_tugas(s2, {"judul": "abc", "prioritas": "tinggi", "estimasi_jam": 1,
                                                       "deadline": date(2026, 11, 14)}, hari_ini))
    print("[GAGAL] Deadline lewat    :", buat_tugas(s2, {"judul": "Tugas lama sekali", "prioritas": "tinggi",
                                                       "estimasi_jam": 1, "deadline": date(2026, 11, 1)}, hari_ini))
    print("Cari T999                 :", cari_tugas(s2, "T999"))
    print("Tugas mendesak            :", tuple(map(lambda x: x["id"], tugas_mendesak(s2))))
    _, s3 = tandai_selesai(s2, "T001")
    print("[BERHASIL] T001 selesai -> mendesak:", tuple(map(lambda x: x["id"], tugas_mendesak(s3))))
    print("[GAGAL] Tandai T999       :", tandai_selesai(s3, "T999"))
    print("Jam kerja per prioritas   :", jam_per_prioritas(s3))
    print("\nTugas belum selesai:")
    print(laporan(s3, hari_ini))
