"""loket.py - Aplikasi 3: pembayaran denda dan sewa, cetak struk.

State: {"tagihan": tuple, "struk": tuple}. Setiap operasi mengembalikan state BARU.
Jalankan sendiri: python loket.py
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

import data
import fplib


def lunas(t: Dict[str, Any]) -> bool:
    """Predikat: tagihan sudah lunas."""
    return t["lunas"]


def cari_tagihan(daftar, tagihan_id: str):
    """Cari tagihan berdasarkan ID; Option."""
    hasil = fplib.where(daftar, lambda t: t["id"] == tagihan_id)
    return fplib.some(hasil[0]) if hasil else fplib.none()


def terima_tagihan(state: Dict[str, Any], tagihan_opsional) -> Dict[str, Any]:
    """Tambahkan tagihan (berupa Option) ke state; none -> state tetap."""
    t = fplib.get_or_else(tagihan_opsional, None)
    return state if t is None else {**state, "tagihan": state["tagihan"] + (t,)}


def tagihan_sewa(booking: Dict[str, Any]) -> Dict[str, Any]:
    """Buat tagihan sewa dari record booking."""
    return {"id": f"TGH-{booking['id']}-S", "jenis": "sewa", "anggota_id": booking["anggota_id"],
            "jumlah": booking["biaya"], "tanggal": booking["mulai"].date(), "lunas": False,
            "keterangan": f"Sewa ruang {booking['ruangan_id']}"}


# ------------------------------------------------------------------- kueri
def tagihan_belum_lunas(state, anggota_id: str) -> tuple:
    """Tagihan milik anggota yang BELUM lunas."""
    return fplib.where(state["tagihan"], fplib.and_(lambda t: t["anggota_id"] == anggota_id, fplib.not_(lunas)))


def tagihan_terbesar(state) -> tuple:
    """Tagihan terurut dari nominal terbesar."""
    return fplib.sort_by(state["tagihan"], lambda t: t["jumlah"], descending=True)


def tagihan_per_jenis(state) -> Dict[str, tuple]:
    """Kelompokkan tagihan per jenis (denda/sewa)."""
    return fplib.group_by(state["tagihan"], lambda t: t["jenis"])


# compose: kelompokkan per jenis lalu jumlahkan nominalnya (dibaca dari kanan ke kiri)
total_per_jenis = fplib.compose(
    lambda grup: {j: fplib.sum_by(ts, lambda t: t["jumlah"]) for j, ts in grup.items()},
    lambda tagihan: fplib.group_by(tagihan, lambda t: t["jenis"]),
)


# ---------------------------------------------------------------- pembayaran
def _cek_tagihan(state):
    """Rule: tagihan harus ada dan belum lunas; sisipkan tagihan ke data."""
    def rule(d):
        t = fplib.get_or_else(cari_tagihan(state["tagihan"], d["tagihan_id"]), None)
        if t is None:
            return fplib.err(f"Tagihan {d['tagihan_id']} tidak ditemukan")
        return fplib.err(f"Tagihan {d['tagihan_id']} sudah lunas") if lunas(t) else fplib.ok({**d, "tagihan": t})
    return rule


def _cek_nominal(d):
    """Rule: nominal bayar harus tepat sama dengan jumlah tagihan."""
    jumlah = d["tagihan"]["jumlah"]
    hasil = fplib.validate(fplib.required("nominal"), fplib.in_range("nominal", jumlah, jumlah))(d)
    return hasil if hasil[0] == "ok" else fplib.err(
        f"Nominal {fplib.format_rupiah(d['nominal'])} tidak sesuai tagihan {fplib.format_rupiah(jumlah)}")


def _catat_bayar(state, t, tanggal) -> tuple:
    """Tandai tagihan lunas (update_where) dan buat struk -> (state_baru, struk)."""
    struk = {"no": f"STR-{len(state['struk']) + 1:03d}", "tagihan_id": t["id"],
             "anggota_id": t["anggota_id"], "jenis": t["jenis"], "jumlah": t["jumlah"], "tanggal": tanggal}
    baru = fplib.update_where(state["tagihan"], lambda x: x["id"] == t["id"], lambda x: fplib.assoc(x, "lunas", True))
    return ({"tagihan": baru, "struk": state["struk"] + (struk,)}, struk)


def bayar(state: Dict[str, Any], tagihan_id: str, nominal: int, tanggal: date):
    """Proses pembayaran -> ok((state_baru, struk)) atau err(pesan)."""
    return fplib.pipe(
        fplib.ok({"tagihan_id": tagihan_id, "nominal": nominal}),
        lambda r: fplib.flat_map(r, _cek_tagihan(state)),
        lambda r: fplib.flat_map(r, _cek_nominal),
        lambda r: fplib.map_result(r, lambda d: _catat_bayar(state, d["tagihan"], tanggal)),
    )


def cetak_struk(struk: Dict[str, Any]) -> str:
    """Hasilkan teks struk (tidak mencetak; print dilakukan pemanggil)."""
    garis = "+" + "-" * 34 + "+"
    baris = (
        f"No. Struk : {struk['no']}",
        f"Tanggal   : {struk['tanggal'].isoformat()}",
        f"Anggota   : {struk['anggota_id']}",
        f"Tagihan   : {struk['tagihan_id']} ({struk['jenis']})",
        f"Dibayar   : {fplib.format_rupiah(struk['jumlah'])}",
        "Status    : LUNAS",
    )
    return "\n".join((garis,) + tuple(map(lambda b: "| " + b.ljust(32) + " |", baris)) + (garis,))


if __name__ == "__main__":
    print("=" * 50, "\n APLIKASI 3: LOKET PEMBAYARAN\n", "=" * 50, sep="")
    hari_ini = date(2026, 11, 11)
    s0 = {"tagihan": data.TAGIHAN_AWAL, "struk": ()}
    print("Tagihan per jenis      :", {k: fplib.format_rupiah(v) for k, v in total_per_jenis(s0["tagihan"]).items()})
    print("Tagihan terbesar       :", tuple(map(lambda t: (t["id"], fplib.format_rupiah(t["jumlah"])), tagihan_terbesar(s0))))
    print("Belum lunas (Budi A002):", tuple(map(lambda t: t["id"], tagihan_belum_lunas(s0, "A002"))))
    print("Cari TGH-999 (Option)  :", fplib.get_or_else(cari_tagihan(s0["tagihan"], "TGH-999"), "tidak ditemukan"))

    print("\n[GAGAL] Budi membayar TGH-001 dengan nominal salah")
    print(" ", bayar(s0, "TGH-001", 1000, hari_ini))
    print("[BERHASIL] Budi membayar TGH-001 sebesar Rp4.000")
    _, (s1, struk) = bayar(s0, "TGH-001", 4000, hari_ini)
    print(cetak_struk(struk))
    print("[GAGAL] Membayar TGH-001 lagi")
    print(" ", bayar(s1, "TGH-001", 4000, hari_ini))
    print("Belum lunas (Budi A002) setelah bayar:", tuple(map(lambda t: t["id"], tagihan_belum_lunas(s1, "A002"))))
