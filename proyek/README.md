# Satu Library, Lima Aplikasi — Praktikum Pemrograman Fungsional (Informatika UMM)

## 1. Deskripsi

Fungsi-fungsi umum bergaya fungsional ditulis **sekali** di satu library, `fplib.py` (tepat **10 fungsi**),
lalu **dipakai ulang** oleh lima aplikasi:

| # | Aplikasi | Fokus |
|---|----------|-------|
| 1 | `perpustakaan.py` | peminjaman, pengembalian, denda |
| 2 | `booking.py` | sewa ruang diskusi per jam, cek bentrok, tolak anggota berdenda |
| 3 | `loket.py` | pembayaran denda/sewa, struk |
| 4 | `keuangan.py` | rekap pemasukan dan pengeluaran |
| 5 | `todo.py` | tugas staf (sebagian dibuat otomatis) |

Syarat: setiap fungsi library benar-benar dipanggil oleh minimal **3 dari 5** aplikasi (lihat bagian 3).

Aturan gaya: pure function, data immutable (tuple/dict baru, tidak dimutasi), tanpa `for`/`while`
di `fplib.py`, `print` hanya di blok `if __name__ == "__main__":` dan `main.py`.
Hasil operasi aplikasi berupa tuple `(True, data)` atau `(False, "pesan error")`.

## 2. Daftar 10 Fungsi

| # | Fungsi | Parameter | Mengembalikan | Contoh |
|---|--------|-----------|---------------|--------|
| 1 | `validate` | `data, rules` (list tuple `(predikat, pesan)`) | `list[str]` pesan error; kosong = valid | `validate({"lama": 30}, [(lambda d: d["lama"] <= 14, "Maks 14 hari")])` → `["Maks 14 hari"]` |
| 2 | `pipe` | `value, *fns` | hasil akhir | `pipe(3, lambda x: x+1, lambda x: x*2)` → `8` |
| 3 | `where` | `items, *predicates` | tuple item yang lolos SEMUA predikat | `where(buku, tersedia, lambda b: b["kategori"] == "Novel")` |
| 4 | `sort_by` | `items, key_fn, descending=False` | tuple baru terurut | `sort_by(tugas, lambda t: t["deadline"])` |
| 5 | `group_by` | `items, key_fn` | `dict {kunci: tuple}` | `group_by(buku, lambda b: b["kategori"])` |
| 6 | `sum_by` | `items, value_fn` | angka | `sum_by(trx, lambda t: t["nominal"])` |
| 7 | `find_by` | `items, predicate, default=None` | item pertama yang cocok / default | `find_by(buku, lambda b: b["id"] == "B001")` |
| 8 | `update_where` | `items, predicate, changes` | tuple baru; item cocok digabung `changes` | `update_where(t, lambda x: x["id"] == "T1", {"lunas": True})` |
| 9 | `format_rupiah` | `angka` | str | `format_rupiah(15000)` → `"Rp15.000"` |
| 10 | `diff_days` | `tanggal_awal, tanggal_akhir` | int | `diff_days(date(2026,11,8), date(2026,11,11))` → `3` |

## 3. Matriks Fungsi × Aplikasi

(✓ = dipanggil lewat `fplib.nama(...)` di file aplikasi tersebut; dihasilkan otomatis dari kode.)

| Fungsi | Perpus | Booking | Loket | Keuangan | Todo | Jumlah |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `validate` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `pipe` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `where` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `sort_by` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `group_by` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `sum_by` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `find_by` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `update_where` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `format_rupiah` | ✓ | ✓ | ✓ | ✓ | – | 4 |
| `diff_days` | ✓ | ✓ | – | – | ✓ | 3 |

## 4. Bukti Pemanggilan (fungsi | file | nomor baris)

| Fungsi | File aplikasi | Nomor baris pemanggilan |
|---|---|---|
| `validate` | `perpustakaan.py` | 54 |
| `validate` | `booking.py` | 47 |
| `validate` | `loket.py` | 68 |
| `validate` | `keuangan.py` | 25 |
| `validate` | `todo.py` | 35 |
| `pipe` | `perpustakaan.py` | 74 |
| `pipe` | `booking.py` | 66 |
| `pipe` | `loket.py` | 75 |
| `pipe` | `keuangan.py` | 90 |
| `pipe` | `todo.py` | 75 |
| `where` | `perpustakaan.py` | 31, 46 |
| `where` | `booking.py` | 34, 41 |
| `where` | `loket.py` | 36 |
| `where` | `keuangan.py` | 43, 48, 62 |
| `where` | `todo.py` | 59, 65, 77 |
| `sort_by` | `perpustakaan.py` | 36 |
| `sort_by` | `booking.py` | 75 |
| `sort_by` | `loket.py` | 41 |
| `sort_by` | `keuangan.py` | 48, 55 |
| `sort_by` | `todo.py` | 59, 78 |
| `group_by` | `perpustakaan.py` | 41 |
| `group_by` | `booking.py` | 80 |
| `group_by` | `loket.py` | 46 |
| `group_by` | `keuangan.py` | 54, 61 |
| `group_by` | `todo.py` | 65, 79 |
| `sum_by` | `perpustakaan.py` | 48 |
| `sum_by` | `booking.py` | 36, 81 |
| `sum_by` | `loket.py` | 47 |
| `sum_by` | `keuangan.py` | 55, 62, 71 |
| `sum_by` | `todo.py` | 66 |
| `find_by` | `perpustakaan.py` | 26, 57, 85 |
| `find_by` | `booking.py` | 29, 70 |
| `find_by` | `loket.py` | 18 |
| `find_by` | `todo.py` | 18 |
| `update_where` | `perpustakaan.py` | 68, 93, 95 |
| `update_where` | `booking.py` | 68 |
| `update_where` | `loket.py` | 53 |
| `update_where` | `todo.py` | 54 |
| `format_rupiah` | `perpustakaan.py` | 79, 107 |
| `format_rupiah` | `booking.py` | 54, 96, 98 |
| `format_rupiah` | `loket.py` | 70, 83, 91, 92 |
| `format_rupiah` | `keuangan.py` | 104 |
| `diff_days` | `perpustakaan.py` | 76 |
| `diff_days` | `booking.py` | 50 |
| `diff_days` | `todo.py` | 23, 31 |

## 5. Cara Menjalankan

Butuh Python 3.10+. Satu-satunya dependensi adalah `pytest`.

```bash
pip install -r requirements.txt

python perpustakaan.py   # demo aplikasi 1
python booking.py        # demo aplikasi 2
python loket.py          # demo aplikasi 3
python keuangan.py       # demo aplikasi 4
python todo.py           # demo aplikasi 5
python main.py           # skenario gabungan 7 langkah
pytest -v                # unit test 10 fungsi
```

## 6. Anggota Kelompok

| No | Nama | NIM | Tugas |
|----|------|-----|-------|
| 1 | (isi nama) | (isi NIM) | (mis. fplib.py + test) |
| 2 | (isi nama) | (isi NIM) | (mis. Perpustakaan) |
| 3 | (isi nama) | (isi NIM) | (mis. Booking & Loket) |
| 4 | (isi nama) | (isi NIM) | (mis. Keuangan & Todo) |
