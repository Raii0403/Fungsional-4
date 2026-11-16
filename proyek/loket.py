"""loket.py - Aplikasi 3: pembayaran denda dan sewa ruangan, cetak struk.

State: {"tagihan": tuple, "struk": tuple}.
"""
from datetime import date
from typing import Any, Dict

from fplib import (Result, compose, err, flat_map, format_rupiah, get_or_else,
                   group_by, in_range, map_result, none, ok, pipe, required,
                   some, sum_by, validate)


def cari_tagihan(daftar, tagihan_id: str):
    """Cari tagihan berdasarkan ID; Option."""
    return next((some(t) for t in daftar if t["id"] == tagihan_id), none())


def terima_tagihan(state: Dict[str, Any], tagihan_opsional) -> Dict[str, Any]:
    """Tambahkan tagihan (berupa Option) ke state; none -> state tetap."""
    t = get_or_else(tagihan_opsional, None)
    return state if t is None else {**state, "tagihan": state["tagihan"] + (t,)}


def tagihan_sewa(booking: Dict[str, Any]) -> Dict[str, Any]:
    """Buat tagihan sewa dari record booking."""
    return {"id": f"TGH-{booking['id']}-S", "jenis": "sewa",
            "anggota_id": booking["anggota_id"], "jumlah": booking["biaya"],
            "tanggal": booking["mulai"].date(), "lunas": False,
            "keterangan": f"Sewa ruang {booking['ruangan_id']}"}


def _catat_bayar(state, t, tanggal) -> tuple:
    """Tandai tagihan lunas dan buat struk -> (state_baru, struk)."""
    struk = {"no": f"STR-{len(state['struk']) + 1:03d}", "tagihan_id": t["id"],
             "anggota_id": t["anggota_id"], "jenis": t["jenis"],
             "jumlah": t["jumlah"], "tanggal": tanggal}
    baru = tuple(map(lambda x: {**x, "lunas": True} if x["id"] == t["id"] else x, state["tagihan"]))
    return ({"tagihan": baru, "struk": state["struk"] + (struk,)}, struk)


def bayar(state: Dict[str, Any], tagihan_id: str, nominal: int, tanggal: date) -> Result:
    """Proses pembayaran -> ok((state_baru, struk)) atau err(pesan)."""
    t = get_or_else(cari_tagihan(state["tagihan"], tagihan_id), None)
    if t is None:
        return err(f"Tagihan {tagihan_id} tidak ditemukan")
    if t["lunas"]:
        return err(f"Tagihan {tagihan_id} sudah lunas")
    validator = validate(required("nominal"), in_range("nominal", t["jumlah"], t["jumlah"]))
    return pipe(
        {"nominal": nominal},
        validator,
        lambda r: r if r[0] == "ok" else err(
            f"Nominal {format_rupiah(nominal)} tidak sesuai tagihan {format_rupiah(t['jumlah'])}"),
        lambda r: map_result(r, lambda _: _catat_bayar(state, t, tanggal)),
    )


def tagihan_per_jenis(state: Dict[str, Any]) -> Dict[str, tuple]:
    """Kelompokkan tagihan per jenis (denda/sewa)."""
    return group_by(state["tagihan"], lambda t: t["jenis"])


# compose: kelompokkan per jenis lalu jumlahkan nominalnya (dibaca dari kanan ke kiri)
total_per_jenis = compose(
    lambda grup: {j: sum_by(ts, lambda t: t["jumlah"]) for j, ts in grup.items()},
    lambda tagihan: group_by(tagihan, lambda t: t["jenis"]),
)


def cetak_struk(struk: Dict[str, Any]) -> str:
    """Hasilkan teks struk (tidak mencetak; print dilakukan pemanggil)."""
    garis = "+" + "-" * 34 + "+"
    baris = (
        f"No. Struk : {struk['no']}",
        f"Tanggal   : {struk['tanggal'].isoformat()}",
        f"Anggota   : {struk['anggota_id']}",
        f"Tagihan   : {struk['tagihan_id']} ({struk['jenis']})",
        f"Dibayar   : {format_rupiah(struk['jumlah'])}",
        "Status    : LUNAS",
    )
    return "\n".join((garis,) + tuple(map(lambda b: "| " + b.ljust(32) + " |", baris)) + (garis,))
