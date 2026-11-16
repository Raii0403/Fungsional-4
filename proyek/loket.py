"""loket.py - Aplikasi 3: pembayaran denda dan sewa, cetak struk.

Hasil operasi berupa tuple (True, data) atau (False, "pesan error").
State: {"tagihan": tuple, "struk": tuple}; setiap operasi mengembalikan state BARU.
Jalankan sendiri: python loket.py
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

import data
import fplib


def cari_tagihan(daftar, tagihan_id: str):
    """Cari tagihan berdasarkan ID; None jika tidak ada."""
    return fplib.find_by(daftar, lambda t: t["id"] == tagihan_id)


def terima_tagihan(state: Dict[str, Any], tagihan) -> Dict[str, Any]:
    """Tambahkan tagihan ke state; jika tagihan None, state tetap."""
    return state if tagihan is None else {**state, "tagihan": state["tagihan"] + (tagihan,)}


def tagihan_sewa(booking: Dict[str, Any]) -> Dict[str, Any]:
    """Buat tagihan sewa dari record booking."""
    return {"id": f"TGH-{booking['id']}-S", "jenis": "sewa", "anggota_id": booking["anggota_id"],
            "jumlah": booking["biaya"], "tanggal": booking["mulai"].date(), "lunas": False,
            "keterangan": f"Sewa ruang {booking['ruangan_id']}"}


# ------------------------------------------------------------------- kueri
def tagihan_belum_lunas(state, anggota_id: str) -> tuple:
    """Tagihan milik anggota yang belum lunas."""
    return fplib.where(state["tagihan"], lambda t: t["anggota_id"] == anggota_id, lambda t: not t["lunas"])


def tagihan_terbesar(state) -> tuple:
    """Tagihan terurut dari nominal terbesar."""
    return fplib.sort_by(state["tagihan"], lambda t: t["jumlah"], descending=True)


def total_per_jenis(state) -> Dict[str, int]:
    """Total tagihan per jenis (denda/sewa)."""
    grup = fplib.group_by(state["tagihan"], lambda t: t["jenis"])
    return {jenis: fplib.sum_by(items, lambda t: t["jumlah"]) for jenis, items in grup.items()}


# --------------------------------------------------------------- pembayaran
def _tandai_lunas(tagihan_id: str):
    """Langkah pipe: tandai satu tagihan lunas."""
    return lambda s: {**s, "tagihan": fplib.update_where(s["tagihan"], lambda t: t["id"] == tagihan_id, {"lunas": True})}


def _tambah_struk(struk: Dict[str, Any]):
    """Langkah pipe: tambahkan struk ke state."""
    return lambda s: {**s, "struk": s["struk"] + (struk,)}


def bayar(state: Dict[str, Any], tagihan_id: str, nominal: int, tanggal: date):
    """Proses pembayaran -> (True, (state_baru, struk)) atau (False, pesan)."""
    t = cari_tagihan(state["tagihan"], tagihan_id)
    if t is None:
        return (False, f"Tagihan {tagihan_id} tidak ditemukan")
    if t["lunas"]:
        return (False, f"Tagihan {tagihan_id} sudah lunas")
    galat = fplib.validate({"nominal": nominal}, [
        (lambda d: d["nominal"] == t["jumlah"],
         f"Nominal {fplib.format_rupiah(nominal)} tidak sesuai tagihan {fplib.format_rupiah(t['jumlah'])}")])
    if galat:
        return (False, "; ".join(galat))
    struk = {"no": f"STR-{len(state['struk']) + 1:03d}", "tagihan_id": t["id"], "anggota_id": t["anggota_id"],
             "jenis": t["jenis"], "jumlah": t["jumlah"], "tanggal": tanggal}
    return (True, (fplib.pipe(state, _tandai_lunas(t["id"]), _tambah_struk(struk)), struk))


def cetak_struk(struk: Dict[str, Any]) -> str:
    """Hasilkan teks struk (tidak mencetak; print dilakukan pemanggil)."""
    garis = "+" + "-" * 34 + "+"
    baris = (f"No. Struk : {struk['no']}", f"Tanggal   : {struk['tanggal'].isoformat()}",
             f"Anggota   : {struk['anggota_id']}", f"Tagihan   : {struk['tagihan_id']} ({struk['jenis']})",
             f"Dibayar   : {fplib.format_rupiah(struk['jumlah'])}", "Status    : LUNAS")
    return "\n".join((garis,) + tuple(map(lambda b: "| " + b.ljust(32) + " |", baris)) + (garis,))


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 3: LOKET PEMBAYARAN\n", "=" * 50, sep="")
    hari_ini = date(2026, 11, 11)
    s0 = {"tagihan": data.TAGIHAN_AWAL, "struk": ()}
    print("Total per jenis        :", {k: fplib.format_rupiah(v) for k, v in total_per_jenis(s0).items()})
    print("Tagihan terbesar       :", tuple(map(lambda t: (t["id"], fplib.format_rupiah(t["jumlah"])), tagihan_terbesar(s0))))
    print("Belum lunas (Budi A002):", tuple(map(lambda t: t["id"], tagihan_belum_lunas(s0, "A002"))))
    print("Cari TGH-999           :", cari_tagihan(s0["tagihan"], "TGH-999"))

    print("\n[GAGAL] Budi membayar TGH-001 dengan nominal salah :", bayar(s0, "TGH-001", 1000, hari_ini))
    print("[BERHASIL] Budi membayar TGH-001 sebesar Rp4.000")
    _, (s1, struk) = bayar(s0, "TGH-001", 4000, hari_ini)
    print(cetak_struk(struk))
    print("[GAGAL] Membayar TGH-001 lagi :", bayar(s1, "TGH-001", 4000, hari_ini))
    print("Belum lunas (Budi) sekarang   :", tuple(map(lambda t: t["id"], tagihan_belum_lunas(s1, "A002"))))
