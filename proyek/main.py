"""main.py - Demo skenario yang menghubungkan kelima aplikasi.

Semua print (efek samping) hanya ada di sini. Setiap langkah menghasilkan
state baru; state lama tidak pernah diubah.
"""
from datetime import date

import booking
import keuangan
import loket
import perpustakaan
import todo
from data import ANGGOTA, BOOKING_AWAL, BUKU, RUANGAN, TRANSAKSI_AWAL, TUGAS_AWAL
from fplib import format_rupiah, some


def judul(teks: str) -> None:
    print(f"\n=== {teks} ===")


def main() -> None:
    hari_ini = date(2026, 11, 11)

    perp0 = {"buku": BUKU, "anggota": ANGGOTA, "peminjaman": ()}
    book0 = {"ruangan": RUANGAN, "booking": BOOKING_AWAL}
    lokt0 = {"tagihan": (), "struk": ()}
    keu0 = TRANSAKSI_AWAL
    todo0 = TUGAS_AWAL

    # ---------------------------------------------------------- Langkah 1
    judul("1. Perpustakaan: Andi telat mengembalikan buku")
    _, (perp1, pinj) = perpustakaan.pinjam(
        perp0, {"anggota_id": "A001", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 1), "lama_hari": 7})
    print(f"Andi meminjam {pinj['buku_id']} ({pinj['id']}), jatuh tempo {pinj['tgl_jatuh_tempo']}")
    coba = perpustakaan.pinjam(
        perp1, {"anggota_id": "A003", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 3), "lama_hari": 7})
    print(f"Citra pinjam B001 pada 2026-11-03 -> {coba}")
    _, (perp2, info) = perpustakaan.kembalikan(perp1, pinj["id"], hari_ini)
    print(f"Dikembalikan {hari_ini}: telat {info['hari_telat']} hari, denda {format_rupiah(info['denda'])}")
    lokt1 = loket.terima_tagihan(lokt0, info["tagihan"])
    print(f"Tagihan di Loket: {tuple(map(lambda t: t['id'], lokt1['tagihan']))}")

    # ---------------------------------------------------------- Langkah 2
    judul("2. Booking: Andi mencoba memesan ruang")
    permintaan = {"anggota_id": "A001", "ruangan_id": "R01", "tanggal": date(2026, 11, 12),
                  "jam_mulai": 11, "durasi": 2}
    print(f"Hasil: {booking.pesan_ruangan(book0, permintaan, lokt1['tagihan'], hari_ini)}")

    # ---------------------------------------------------------- Langkah 3
    judul("3. Loket: Andi membayar denda")
    tid = lokt1["tagihan"][0]["id"]
    print(f"Bayar {format_rupiah(3000)} -> {loket.bayar(lokt1, tid, 3000, hari_ini)}")
    _, (lokt2, struk) = loket.bayar(lokt1, tid, 6000, hari_ini)
    print(loket.cetak_struk(struk))

    # ---------------------------------------------------------- Langkah 4
    judul("4. Keuangan: pembayaran dicatat sebagai pemasukan")
    _, (keu1, trx) = keuangan.catat_dari_struk(keu0, struk)
    print(f"Tercatat {trx['id']}: {trx['kategori']} {format_rupiah(trx['nominal'])} ({trx['keterangan']})")
    print(f"Coba catat kategori salah -> {keuangan.catat(keu1, {'tanggal': hari_ini, 'kategori': 'hadiah', 'nominal': 1000, 'keterangan': 'uji'})}")

    # ---------------------------------------------------------- Langkah 5
    judul("5. Todo: tugas otomatis dari sistem")
    _, (todo1, tugas) = todo.buat_tugas_otomatis(todo0, "Buka blokir anggota Andi", hari_ini)
    print(f"Dibuat {tugas['id']}: {tugas['judul']} (prioritas {tugas['prioritas']}, deadline {tugas['deadline']})")
    bentrok = todo.tugas_bentrok(todo1, tugas)
    print(f"Periode tumpang tindih dengan: {tuple(map(lambda t: t['id'], bentrok))}")

    # ---------------------------------------------------------- Langkah 6
    judul("6. Booking: Andi mencoba lagi")
    bentrok_req = {**permintaan, "jam_mulai": 10}
    print(f"Jam 10:00 -> {booking.pesan_ruangan(book0, bentrok_req, lokt2['tagihan'], hari_ini)}")
    _, (book1, bk) = booking.pesan_ruangan(book0, permintaan, lokt2["tagihan"], hari_ini)
    print(f"Jam 11:00 berhasil: {bk['id']} {bk['mulai']:%Y-%m-%d %H:%M}-{bk['selesai']:%H:%M}, biaya {format_rupiah(bk['biaya'])}")
    lokt3 = loket.terima_tagihan(lokt2, some(loket.tagihan_sewa(bk)))
    print(f"Tagihan di Loket: {tuple(map(lambda t: (t['id'], t['jenis'], format_rupiah(t['jumlah']), 'lunas' if t['lunas'] else 'belum'), lokt3['tagihan']))}")

    # ---------------------------------------------------------- Langkah 7
    judul("7. Laporan akhir")
    print("[Keuangan]")
    print(keuangan.laporan(keu1))
    print("\n[Todo per prioritas]")
    print(todo.laporan(todo1, hari_ini))

    judul("Ringkasan tambahan")
    print("Buku per kategori :", {k: tuple(map(lambda b: b['judul'], v)) for k, v in perpustakaan.buku_per_kategori(BUKU).items()})
    print("Jumlah buku/kat. :", perpustakaan.jumlah_buku_per_kategori(BUKU))
    print("Jumlah tugas/prio.:", todo.jumlah_per_prioritas(todo1))
    print("Pendapatan ruangan:", {k: format_rupiah(v) for k, v in booking.pendapatan_per_ruangan(book1).items()})
    print("Tagihan per jenis :", {k: format_rupiah(v) for k, v in loket.total_per_jenis(lokt3["tagihan"]).items()})


if __name__ == "__main__":
    main()
