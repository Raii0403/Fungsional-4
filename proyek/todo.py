"""todo.py - Aplikasi 5: tugas staf (sebagian dibuat otomatis oleh sistem lain).

State: tuple tugas (immutable). Setiap operasi mengembalikan tuple baru.
Jalankan sendiri: python todo.py
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

import data
import fplib


# ----------------------------------------------------------------- predikat
def selesai(t: Dict[str, Any]) -> bool:
    """Predikat: tugas sudah selesai."""
    return t["selesai"]


def prioritas(nama: str):
    """Pabrik predikat: tugas berprioritas tertentu."""
    return lambda t: t["prioritas"] == nama


def _prioritas_valid(d):
    """Rule: prioritas harus tinggi/sedang/rendah."""
    return fplib.ok(d) if d.get("prioritas") in data.PRIORITAS else fplib.err("Prioritas harus tinggi, sedang, atau rendah")


def _deadline_valid(hari_ini: date):
    """Rule: deadline tidak boleh sebelum hari ini."""
    return lambda d: fplib.ok(d) if fplib.diff_days(hari_ini, d["deadline"]) >= 0 else fplib.err("Deadline sudah lewat")


def _cek_duplikat(daftar: tuple):
    """Rule: tolak tugas aktif dengan judul yang sama."""
    return lambda d: (fplib.err(f"Tugas '{d['judul']}' sudah ada")
                      if fplib.where(daftar, fplib.and_(fplib.not_(selesai), lambda t: t["judul"] == d["judul"]))
                      else fplib.ok(d))


def cari_tugas(daftar: tuple, tugas_id: str):
    """Cari tugas berdasarkan ID; Option."""
    hasil = fplib.where(daftar, lambda t: t["id"] == tugas_id)
    return fplib.some(hasil[0]) if hasil else fplib.none()


def sisa_hari(tugas: Dict[str, Any], hari_ini: date) -> int:
    """Sisa hari menuju deadline."""
    return fplib.diff_days(hari_ini, tugas["deadline"])


# --------------------------------------------------------------------- proses
def _simpan(daftar, d, hari_ini) -> tuple:
    """Bentuk record tugas dan tuple baru."""
    rec = {"id": f"T{len(daftar) + 1:03d}", "judul": d["judul"], "prioritas": d["prioritas"],
           "mulai": hari_ini, "deadline": d["deadline"], "otomatis": d.get("otomatis", False), "selesai": False}
    return (daftar + (rec,), rec)


def buat_tugas(daftar: tuple, d: Dict[str, Any], hari_ini: date):
    """Tambah tugas -> ok((daftar_baru, tugas)) atau err(pesan)."""
    return fplib.pipe(
        d,
        fplib.validate(fplib.required("judul"), fplib.min_length("judul", 5), fplib.required("deadline"),
                       _deadline_valid(hari_ini), _prioritas_valid),
        lambda r: fplib.flat_map(r, _cek_duplikat(daftar)),
        lambda r: fplib.map_result(r, lambda x: _simpan(daftar, x, hari_ini)),
    )


def buat_tugas_otomatis(daftar: tuple, judul: str, hari_ini: date, prio: str = "tinggi"):
    """Tugas otomatis dari sistem lain; deadline besok."""
    return buat_tugas(daftar, {"judul": judul, "prioritas": prio,
                               "deadline": hari_ini + timedelta(days=1), "otomatis": True}, hari_ini)


def tandai_selesai(daftar: tuple, tugas_id: str):
    """Tandai tugas selesai -> ok(daftar_baru) atau err(pesan)."""
    t = fplib.get_or_else(cari_tugas(daftar, tugas_id), None)
    return fplib.err(f"Tugas {tugas_id} tidak ditemukan") if t is None else fplib.ok(
        fplib.update_where(daftar, lambda x: x["id"] == tugas_id, lambda x: fplib.assoc(x, "selesai", True)))


# ---------------------------------------------------------------------- kueri
def tugas_bentrok(daftar: tuple, tugas: Dict[str, Any]) -> tuple:
    """Tugas aktif lain yang periodenya beririsan dengan tugas ini."""
    return fplib.where(daftar, fplib.and_(
        fplib.not_(selesai), lambda t: t["id"] != tugas["id"],
        lambda t: fplib.is_overlap(t["mulai"], t["deadline"], tugas["mulai"], tugas["deadline"])))


def tugas_mendesak(daftar: tuple) -> tuple:
    """Tugas belum selesai DAN prioritas tinggi, urut deadline terdekat."""
    return fplib.sort_by(fplib.where(daftar, fplib.and_(fplib.not_(selesai), prioritas("tinggi"))),
                         lambda t: t["deadline"])


def per_prioritas(daftar: tuple) -> Dict[str, tuple]:
    """Kelompokkan tugas per prioritas."""
    return fplib.group_by(daftar, lambda t: t["prioritas"])


# compose: kelompokkan per prioritas, lalu hitung jumlah tugas tiap prioritas
jumlah_per_prioritas = fplib.compose(
    lambda grup: {p: fplib.sum_by(v, lambda _: 1) for p, v in grup.items()},
    per_prioritas,
)


def laporan(daftar: tuple, hari_ini: date) -> str:
    """Teks daftar tugas per prioritas, tiap kelompok urut deadline terdekat."""
    grup = per_prioritas(daftar)
    baris = lambda t: (f"    [{'x' if t['selesai'] else ' '}] {t['id']} {t['judul']} "
                       f"(deadline {t['deadline']}, sisa {sisa_hari(t, hari_ini)} hari)"
                       + (" [otomatis]" if t["otomatis"] else ""))
    bagian = lambda p: (f"  Prioritas {p.upper()}:",) + tuple(map(baris, fplib.sort_by(grup[p], lambda t: t["deadline"])))
    return "\n".join(sum(map(bagian, fplib.where(data.PRIORITAS, lambda p: p in grup)), ()))


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 5: TODO STAF\n", "=" * 50, sep="")
    hari_ini = date(2026, 11, 11)
    s0 = data.TUGAS_AWAL
    print("[BERHASIL] Tugas manual")
    _, (s1, t) = buat_tugas(s0, {"judul": "Siapkan laporan bulanan", "prioritas": "tinggi",
                                 "deadline": date(2026, 11, 14)}, hari_ini)
    print(f"  {t['id']} {t['judul']} (sisa {sisa_hari(t, hari_ini)} hari)")
    print("[BERHASIL] Tugas otomatis dari sistem lain")
    _, (s2, t2) = buat_tugas_otomatis(s1, "Buka blokir anggota Andi", hari_ini)
    print(f"  {t2['id']} {t2['judul']} [otomatis={t2['otomatis']}]")
    print("[GAGAL] Judul terlalu pendek:", buat_tugas(s2, {"judul": "abc", "prioritas": "tinggi", "deadline": date(2026, 11, 14)}, hari_ini))
    print("[GAGAL] Deadline sudah lewat:", buat_tugas(s2, {"judul": "Tugas lama sekali", "prioritas": "tinggi", "deadline": date(2026, 11, 1)}, hari_ini))
    print("[GAGAL] Tugas ganda         :", buat_tugas(s2, {"judul": "Pesan buku baru", "prioritas": "sedang", "deadline": date(2026, 11, 25)}, hari_ini))
    print("Cari T999 (Option)          :", fplib.get_or_else(cari_tugas(s2, "T999"), "tidak ditemukan"))
    print("Tugas mendesak              :", tuple(map(lambda x: x["id"], tugas_mendesak(s2))))
    print("[BERHASIL] Tandai T001 selesai")
    _, s3 = tandai_selesai(s2, "T001")
    print("Tugas mendesak setelahnya   :", tuple(map(lambda x: x["id"], tugas_mendesak(s3))))
    print("[GAGAL] Tandai T999         :", tandai_selesai(s3, "T999"))
    print("Jumlah per prioritas        :", jumlah_per_prioritas(s3))
    print()
    print(laporan(s3, hari_ini))
