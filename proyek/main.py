"""main.py - Demo skenario gabungan kelima aplikasi.

Semua print (efek samping) hanya ada di sini. Setiap langkah menghasilkan
state baru; state lama tidak pernah diubah.
"""
from datetime import date

import booking
import data
import fplib
import keuangan
import loket
import perpustakaan
import todo


def judul(teks: str) -> None:
    print(f"\n=== {teks} ===")


def main() -> None:
    hari_ini = date(2026, 11, 11)
    perp0 = {"buku": data.BUKU, "anggota": data.ANGGOTA, "peminjaman": ()}
    book0 = {"ruangan": data.RUANGAN, "booking": data.BOOKING_AWAL}
    lokt0 = {"tagihan": (), "struk": ()}

    judul("1. Perpustakaan: Andi telat mengembalikan buku")
    _, (perp1, pinj) = perpustakaan.pinjam(
        perp0, {"anggota_id": "A001", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 1), "lama_hari": 7})
    print(f"Andi meminjam {pinj['buku_id']} ({pinj['id']}), jatuh tempo {pinj['tgl_jatuh_tempo']}")
    _, (perp2, info) = perpustakaan.kembalikan(perp1, pinj["id"], hari_ini)
    print(f"Dikembalikan {hari_ini}: telat {info['hari_telat']} hari, denda {fplib.format_rupiah(info['denda'])}")
    lokt1 = loket.terima_tagihan(lokt0, info["tagihan"])
    print("Tagihan di Loket:", tuple(map(lambda t: t["id"], lokt1["tagihan"])))

    judul("2. Booking: Andi mencoba memesan ruang")
    permintaan = {"anggota_id": "A001", "ruangan_id": "R01", "tanggal": date(2026, 11, 12),
                  "jam_mulai": 11, "durasi": 2, "peserta": 4}
    print("Hasil:", booking.pesan_ruangan(book0, permintaan, lokt1["tagihan"], hari_ini))

    judul("3. Loket: Andi membayar denda")
    tid = lokt1["tagihan"][0]["id"]
    print(f"Bayar {fplib.format_rupiah(3000)} ->", loket.bayar(lokt1, tid, 3000, hari_ini))
    _, (lokt2, struk) = loket.bayar(lokt1, tid, 6000, hari_ini)
    print(loket.cetak_struk(struk))
    print("Tagihan Andi yang belum lunas:", loket.tagihan_belum_lunas(lokt2, "A001"))

    judul("4. Keuangan: pembayaran dicatat sebagai pemasukan")
    _, (keu1, trx) = keuangan.catat_dari_struk(data.TRANSAKSI_AWAL, struk)
    print(f"Tercatat {trx['id']}: {trx['kategori']} {fplib.format_rupiah(trx['nominal'])} ({trx['keterangan']})")

    judul("5. Todo: tugas otomatis dari sistem")
    _, (todo1, tugas) = todo.buat_tugas_otomatis(data.TUGAS_AWAL, "Buka blokir anggota Andi", hari_ini)
    print(f"Dibuat {tugas['id']}: {tugas['judul']} (prioritas {tugas['prioritas']}, deadline {tugas['deadline']})")
    print("Periode tumpang tindih dengan:", tuple(map(lambda t: t["id"], todo.tugas_bentrok(todo1, tugas))))

    judul("6. Booking: Andi mencoba lagi")
    print("Jam 10:00 ->", booking.pesan_ruangan(book0, {**permintaan, "jam_mulai": 10}, lokt2["tagihan"], hari_ini))
    _, (book1, bk) = booking.pesan_ruangan(book0, permintaan, lokt2["tagihan"], hari_ini)
    print(f"Jam 11:00 berhasil: {bk['id']} {bk['mulai']:%Y-%m-%d %H:%M}-{bk['selesai']:%H:%M}, "
          f"status {bk['status']}, biaya {fplib.format_rupiah(bk['biaya'])}")
    lokt3 = loket.terima_tagihan(lokt2, fplib.some(loket.tagihan_sewa(bk)))
    print("Tagihan di Loket:", tuple(map(
        lambda t: (t["id"], t["jenis"], fplib.format_rupiah(t["jumlah"]), "lunas" if t["lunas"] else "belum"),
        lokt3["tagihan"])))

    judul("7. Laporan akhir")
    print("[Keuangan]")
    print(keuangan.laporan(keu1))
    print("\n[Todo per prioritas, urut deadline]")
    print(todo.laporan(todo1, hari_ini))

    judul("Ringkasan tambahan")
    print("Jumlah buku per kategori :", perpustakaan.jumlah_buku_per_kategori(data.BUKU))
    print("Pendapatan ruangan       :", {k: fplib.format_rupiah(v) for k, v in booking.pendapatan_per_ruangan(book1).items()})
    print("Tagihan per jenis        :", {k: fplib.format_rupiah(v) for k, v in loket.total_per_jenis(lokt3["tagihan"]).items()})
    print("Jumlah tugas per prior.  :", todo.jumlah_per_prioritas(todo1))


if __name__ == "__main__":
    main()
