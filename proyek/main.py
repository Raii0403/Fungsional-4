"""main.py - Demo gabungan kelima aplikasi.

  python main.py               -> demo skenario otomatis (Andi, 7 langkah)
  python main.py --interaktif  -> simulasi interaktif dengan input dari pengguna

Semua print/input (efek samping) hanya ada di file ini. Setiap langkah
menghasilkan state baru; state lama tidak pernah diubah.
"""
import sys
from datetime import date, timedelta

import booking
import data
import fplib
import keuangan
import loket
import perpustakaan
import todo


def judul(teks: str) -> None:
    print(f"\n=== {teks} ===")


# ====================================================================
# MODE 1: DEMO SKENARIO OTOMATIS
# ====================================================================
def demo() -> None:
    hari_ini = date(2026, 11, 11)
    perp0 = {"buku": data.BUKU, "anggota": data.ANGGOTA, "peminjaman": ()}
    book0 = {"ruangan": data.RUANGAN, "booking": data.BOOKING_AWAL}
    lokt0 = {"tagihan": (), "struk": ()}

    judul("1. Perpustakaan: Andi telat mengembalikan buku")
    _, (perp1, pinj) = perpustakaan.pinjam(
        perp0, {"anggota_id": "A001", "buku_id": "B001", "tgl_pinjam": date(2026, 11, 1), "lama_hari": 7})
    print(f"Andi meminjam {pinj['buku_id']} ({pinj['id']}), jatuh tempo {pinj['tgl_jatuh_tempo']}")
    _, (perp2, info, tagihan) = perpustakaan.kembalikan(perp1, pinj["id"], hari_ini)
    print(f"Dikembalikan {hari_ini}: telat {info['hari_telat']} hari, denda {info['teks']}")
    lokt1 = loket.terima_tagihan(lokt0, tagihan)
    print("Tagihan di Loket:", tuple(map(lambda t: t["id"], lokt1["tagihan"])))

    judul("2. Booking: Andi mencoba memesan ruang")
    permintaan = {"anggota_id": "A001", "ruangan_id": "R01", "tanggal": date(2026, 11, 12), "jam_mulai": 11, "durasi": 2}
    print("Hasil:", booking.pesan_ruangan(book0, permintaan, lokt1["tagihan"], hari_ini))

    judul("3. Loket: Andi membayar denda")
    tid = lokt1["tagihan"][0]["id"]
    print(f"Bayar {fplib.format_rupiah(3000)} ->", loket.bayar(lokt1, tid, 3000, hari_ini))
    _, (lokt2, struk) = loket.bayar(lokt1, tid, 6000, hari_ini)
    print(loket.cetak_struk(struk))

    judul("4. Keuangan: pembayaran dicatat sebagai pemasukan")
    _, (keu1, trx) = keuangan.catat_dari_struk(data.TRANSAKSI_AWAL, struk)
    print(f"Tercatat {trx['id']}: {trx['kategori']} {fplib.format_rupiah(trx['nominal'])} ({trx['keterangan']})")

    judul("5. Todo: tugas otomatis dari sistem")
    _, (todo1, tugas) = todo.buat_tugas_otomatis(data.TUGAS_AWAL, "Buka blokir anggota Andi", hari_ini)
    print(f"Dibuat {tugas['id']}: {tugas['judul']} (prioritas {tugas['prioritas']}, deadline {tugas['deadline']})")

    judul("6. Booking: Andi mencoba lagi")
    print("Jam 10:00 ->", booking.pesan_ruangan(book0, {**permintaan, "jam_mulai": 10}, lokt2["tagihan"], hari_ini))
    _, (_, bk) = booking.pesan_ruangan(book0, permintaan, lokt2["tagihan"], hari_ini)
    print(f"Jam 11:00 berhasil: {bk['id']} {bk['mulai']:%Y-%m-%d %H:%M}-{bk['selesai']:%H:%M}, "
          f"status {bk['status']}, biaya {fplib.format_rupiah(bk['biaya'])}")
    lokt3 = loket.terima_tagihan(lokt2, loket.tagihan_sewa(bk))
    print("Tagihan di Loket:", tuple(map(
        lambda t: (t["id"], t["jenis"], fplib.format_rupiah(t["jumlah"]), "lunas" if t["lunas"] else "belum"),
        lokt3["tagihan"])))

    judul("7. Laporan akhir")
    print("[Keuangan]")
    print(keuangan.laporan(keu1))
    print("\n[Todo per prioritas]")
    print(todo.laporan(todo1, hari_ini))


# ====================================================================
# MODE 2: SIMULASI INTERAKTIF
# Setiap aksi menerima state + masukan, lalu mengembalikan (state_baru, pesan).
# ====================================================================
MENU = """
------------------------------------------------
 SIMULASI PERPUSTAKAAN TERPADU   (tanggal: {tgl})
------------------------------------------------
 1. Lihat katalog buku & peminjaman aktif
 2. Pinjam buku
 3. Kembalikan buku
 4. Booking ruang diskusi
 5. Lihat tagihan di loket
 6. Bayar tagihan
 7. Laporan keuangan
 8. Daftar tugas staf
 9. Majukan tanggal simulasi
 0. Keluar"""


def angka(teks: str):
    """Ubah teks menjadi int; None jika bukan angka."""
    try:
        return int(teks)
    except ValueError:
        return None


def tanggal(teks: str):
    """Ubah 'YYYY-MM-DD' menjadi date; None jika formatnya salah."""
    try:
        return date.fromisoformat(teks)
    except ValueError:
        return None


def keadaan_awal() -> dict:
    """State awal seluruh sistem."""
    return {"perp": {"buku": data.BUKU, "anggota": data.ANGGOTA, "peminjaman": ()},
            "book": {"ruangan": data.RUANGAN, "booking": data.BOOKING_AWAL},
            "lokt": {"tagihan": data.TAGIHAN_AWAL, "struk": ()},
            "keu": data.TRANSAKSI_AWAL, "todo": data.TUGAS_AWAL, "hari_ini": date(2026, 11, 10)}


def teks_katalog(s: dict) -> str:
    """Teks katalog buku dan peminjaman aktif."""
    buku = tuple(f"  {b['id']} {b['judul']:<24} [{b['kategori']}] {b['status']}" for b in s["perp"]["buku"])
    aktif = fplib.where(s["perp"]["peminjaman"], lambda p: p["tgl_kembali"] is None)
    pinj = tuple(f"  {p['id']}: buku {p['buku_id']} oleh {p['anggota_id']}, jatuh tempo {p['tgl_jatuh_tempo']}"
                 for p in aktif) or ("  (tidak ada)",)
    anggota = tuple(f"{a['id']}={a['nama']}" for a in s["perp"]["anggota"])
    return "\n".join(("Anggota: " + ", ".join(anggota), "Katalog:") + buku + ("Peminjaman aktif:",) + pinj)


def teks_tagihan(s: dict) -> str:
    """Teks daftar tagihan, terbesar dulu."""
    baris = tuple(f"  {t['id']:<12} {t['anggota_id']} {t['jenis']:<6} {fplib.format_rupiah(t['jumlah']):>10}  "
                  f"{'LUNAS' if t['lunas'] else 'belum'}" for t in loket.tagihan_terbesar(s["lokt"]))
    return "\n".join(("Tagihan:",) + (baris or ("  (kosong)",)))


def aksi_pinjam(s: dict, anggota_id: str, buku_id: str, lama: str):
    """Pinjam buku mulai tanggal simulasi -> (state_baru, pesan)."""
    if angka(lama) is None:
        return (s, "GAGAL: lama pinjam harus berupa angka")
    hasil = perpustakaan.pinjam(s["perp"], {"anggota_id": anggota_id, "buku_id": buku_id,
                                            "tgl_pinjam": s["hari_ini"], "lama_hari": angka(lama)})
    if not hasil[0]:
        return (s, f"GAGAL: {hasil[1]}")
    perp, rec = hasil[1]
    return ({**s, "perp": perp}, f"BERHASIL: {rec['id']}, jatuh tempo {rec['tgl_jatuh_tempo']}")


def aksi_kembali(s: dict, peminjaman_id: str):
    """Kembalikan buku pada tanggal simulasi; denda menjadi tagihan di loket."""
    hasil = perpustakaan.kembalikan(s["perp"], peminjaman_id, s["hari_ini"])
    if not hasil[0]:
        return (s, f"GAGAL: {hasil[1]}")
    perp, info, tagihan = hasil[1]
    pesan = (f"BERHASIL: telat {info['hari_telat']} hari, denda {info['teks']}"
             + (f" -> tagihan {tagihan['id']} dibuat di Loket" if tagihan else " (tepat waktu, tanpa denda)"))
    return ({**s, "perp": perp, "lokt": loket.terima_tagihan(s["lokt"], tagihan)}, pesan)


def aksi_booking(s: dict, anggota_id: str, ruangan_id: str, tgl: str, jam: str, durasi: str):
    """Booking ruang; jika berhasil, tagihan sewa masuk ke loket."""
    if tanggal(tgl) is None or angka(jam) is None or angka(durasi) is None:
        return (s, "GAGAL: tanggal (YYYY-MM-DD), jam, dan durasi harus diisi dengan format benar")
    hasil = booking.pesan_ruangan(s["book"], {"anggota_id": anggota_id, "ruangan_id": ruangan_id,
                                              "tanggal": tanggal(tgl), "jam_mulai": angka(jam),
                                              "durasi": angka(durasi)}, s["lokt"]["tagihan"], s["hari_ini"])
    if not hasil[0]:
        return (s, f"GAGAL: {hasil[1]}")
    book, bk = hasil[1]
    return ({**s, "book": book, "lokt": loket.terima_tagihan(s["lokt"], loket.tagihan_sewa(bk))},
            f"BERHASIL: {bk['id']} {bk['mulai']:%d/%m %H:%M}-{bk['selesai']:%H:%M}, biaya "
            f"{fplib.format_rupiah(bk['biaya'])} -> tagihan sewa dibuat di Loket")


def aksi_bayar(s: dict, tagihan_id: str, nominal: str):
    """Bayar tagihan -> struk, catat ke keuangan, dan buat tugas buka blokir bila denda anggota sudah lunas."""
    if angka(nominal) is None:
        return (s, "GAGAL: nominal harus berupa angka")
    hasil = loket.bayar(s["lokt"], tagihan_id, angka(nominal), s["hari_ini"])
    if not hasil[0]:
        return (s, f"GAGAL: {hasil[1]}")
    lokt, struk = hasil[1]
    keu = keuangan.catat_dari_struk(s["keu"], struk)[1][0]
    sisa_denda = fplib.where(lokt["tagihan"], lambda t: t["anggota_id"] == struk["anggota_id"],
                             lambda t: t["jenis"] == "denda", lambda t: not t["lunas"])
    nama = fplib.find_by(s["perp"]["anggota"], lambda a: a["id"] == struk["anggota_id"])["nama"]
    buka = struk["jenis"] == "denda" and not sisa_denda
    todo_baru = todo.buat_tugas_otomatis(s["todo"], f"Buka blokir anggota {nama}", s["hari_ini"])[1][0] if buka else s["todo"]
    return ({**s, "lokt": lokt, "keu": keu, "todo": todo_baru},
            loket.cetak_struk(struk) + ("\nTugas otomatis dibuat: Buka blokir anggota " + nama if buka else ""))


def aksi_majukan(s: dict, hari: str):
    """Majukan tanggal simulasi sejumlah hari."""
    if angka(hari) is None or angka(hari) < 0:
        return (s, "GAGAL: jumlah hari harus angka >= 0")
    baru = s["hari_ini"] + timedelta(days=angka(hari))
    return ({**s, "hari_ini": baru}, f"Tanggal simulasi sekarang {baru}")


def interaktif() -> None:
    """Loop menu interaktif; membaca input dan mencetak hasil."""
    s = keadaan_awal()
    tanya = lambda teks: input(teks).strip()
    while True:  # loop antarmuka pengguna (bukan pengolahan data), sah di main.py
        print(MENU.format(tgl=s["hari_ini"]))
        try:
            pilih = tanya("Pilih menu: ")
            if pilih == "0":
                print("Sampai jumpa!")
                return
            elif pilih == "1":
                print(teks_katalog(s))
            elif pilih == "2":
                s, pesan = aksi_pinjam(s, tanya("ID anggota (mis. A001): "), tanya("ID buku (mis. B001): "),
                                       tanya("Lama pinjam (hari, 1-14): "))
                print(pesan)
            elif pilih == "3":
                print(teks_katalog(s))
                s, pesan = aksi_kembali(s, tanya("ID peminjaman (mis. P001): "))
                print(pesan)
            elif pilih == "4":
                s, pesan = aksi_booking(s, tanya("ID anggota: "), tanya("ID ruangan (R01/R02): "),
                                        tanya("Tanggal (YYYY-MM-DD): "), tanya("Jam mulai (8-18): "),
                                        tanya("Durasi (jam, 1-4): "))
                print(pesan)
            elif pilih == "5":
                print(teks_tagihan(s))
            elif pilih == "6":
                print(teks_tagihan(s))
                s, pesan = aksi_bayar(s, tanya("ID tagihan: "), tanya("Nominal bayar (angka): "))
                print(pesan)
            elif pilih == "7":
                print(keuangan.laporan(s["keu"]))
            elif pilih == "8":
                print(todo.laporan(s["todo"], s["hari_ini"]))
            elif pilih == "9":
                s, pesan = aksi_majukan(s, tanya("Majukan berapa hari: "))
                print(pesan)
            else:
                print("Menu tidak dikenal.")
        except EOFError:
            print("\nInput berakhir, keluar.")
            return


if __name__ == "__main__":
    interaktif() if "--interaktif" in sys.argv else demo()
