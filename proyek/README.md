# Satu Library, Lima Aplikasi — Praktikum Pemrograman Fungsional (Informatika UMM)

## 1. Deskripsi

Proyek ini memperlihatkan bahwa fungsi-fungsi umum bergaya fungsional dapat ditulis **sekali** di satu
library (`fplib.py`, 10 kelompok, 25 fungsi) lalu **dipakai ulang** oleh lima aplikasi berbeda:

| # | Aplikasi | Fokus |
|---|----------|-------|
| 1 | `perpustakaan.py` | peminjaman, pengembalian, denda |
| 2 | `booking.py` | sewa ruang diskusi per jam, cek bentrok, blokir anggota berdenda |
| 3 | `loket.py` | pembayaran denda/sewa, struk |
| 4 | `keuangan.py` | rekap pemasukan dan pengeluaran |
| 5 | `todo.py` | tugas staf (sebagian otomatis) |

Syarat: setiap fungsi library dipakai minimal **3 dari 5** aplikasi (lihat matriks pada bagian 3).
Aturan gaya: pure function, data immutable (tuple/dict baru, tidak ada mutasi), tanpa `for`/`while` di
`fplib.py`, `print` hanya di blok `if __name__ == "__main__":` dan `main.py`.

## 2. Daftar 10 Kelompok Fungsi

Representasi: `Result` = `("ok", nilai)` / `("err", pesan)`; `Option` = `("some", nilai)` / `("none", None)`.

| # | Fungsi | Parameter | Mengembalikan | Contoh |
|---|--------|-----------|---------------|--------|
| 1 | `ok` | `value` | Result ok | `ok(5)` → `("ok", 5)` |
| 1 | `err` | `message` | Result err | `err("gagal")` → `("err", "gagal")` |
| 1 | `map_result` | `result, fn` | Result | `map_result(ok(2), lambda x: x*10)` → `("ok", 20)` |
| 1 | `flat_map` | `result, fn` (fn → Result) | Result | `flat_map(ok(4), lambda x: ok(x+1))` → `("ok", 5)` |
| 2 | `pipe` | `value, *fns` | hasil akhir | `pipe(3, f, g)` = `g(f(3))` |
| 2 | `compose` | `*fns` | fungsi baru (kanan→kiri) | `compose(f, g)(3)` = `f(g(3))` |
| 3 | `validate` | `*rules` | validator `data → Result` | `validate(required("a"))({"a": 1})` → `ok(...)` |
| 3 | `required` | `field` | rule | `required("judul")` |
| 3 | `in_range` | `field, min, max` | rule | `in_range("durasi", 1, 4)` |
| 3 | `min_length` | `field, n` | rule | `min_length("judul", 5)` |
| 4 | `group_by` | `items, key_fn` | `dict {key: tuple}` | `group_by(buku, lambda b: b["kategori"])` |
| 4 | `sum_by` | `items, value_fn` | angka | `sum_by(trx, lambda t: t["nominal"])` |
| 5 | `format_rupiah` | `angka` | str | `format_rupiah(15000)` → `"Rp15.000"` |
| 6 | `some` | `value` | Option | `some(1)` → `("some", 1)` |
| 6 | `none` | – | Option | `none()` → `("none", None)` |
| 6 | `get_or_else` | `option, default` | nilai | `get_or_else(none(), 0)` → `0` |
| 7 | `diff_days` | `tanggal_awal, tanggal_akhir` | int | `diff_days(date(2026,11,8), date(2026,11,11))` → `3` |
| 7 | `is_overlap` | `mulai1, selesai1, mulai2, selesai2` | bool | `is_overlap(9, 11, 10, 12)` → `True` |
| 8 | `sort_by` | `items, key_fn, descending=False` | tuple baru | `sort_by(t, lambda x: x["deadline"])` |
| 8 | `top_n` | `items, key_fn, n` | tuple n teratas | `top_n(buku, lambda b: b["jumlah_pinjam"], 2)` |
| 9 | `where` | `items, predicate` | tuple baru | `where(buku, and_(tersedia, kategori("Novel")))` |
| 9 | `and_` | `*predicates` | predikat baru | `and_(p, q)(x)` = `p(x) and q(x)` |
| 9 | `not_` | `predicate` | predikat baru | `where(buku, not_(tersedia))` |
| 10 | `assoc` | `record, key, value` | dict BARU | `assoc(b, "status", "dipinjam")` |
| 10 | `update_where` | `items, predicate, updater` | tuple baru | `update_where(t, lambda x: x["id"]=="T1", lambda x: assoc(x,"lunas",True))` |

## 3. Matriks Fungsi × Aplikasi

(✓ = dipanggil lewat `fplib.nama(...)` di file aplikasi tersebut; dihasilkan otomatis dari kode.)

| Fungsi | Perpus | Booking | Loket | Keuangan | Todo | Jumlah |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `ok` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `err` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `map_result` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `flat_map` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `pipe` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `compose` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `validate` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `required` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `in_range` | ✓ | ✓ | ✓ | ✓ | – | 4 |
| `min_length` | ✓ | ✓ | – | ✓ | ✓ | 4 |
| `group_by` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `sum_by` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `format_rupiah` | ✓ | ✓ | ✓ | ✓ | – | 4 |
| `some` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `none` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `get_or_else` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `diff_days` | ✓ | ✓ | – | – | ✓ | 3 |
| `is_overlap` | ✓ | ✓ | – | – | ✓ | 3 |
| `sort_by` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `top_n` | ✓ | ✓ | – | ✓ | – | 3 |
| `where` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `and_` | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| `not_` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `assoc` | ✓ | ✓ | ✓ | – | ✓ | 4 |
| `update_where` | ✓ | ✓ | ✓ | – | ✓ | 4 |

## 4. Bukti Pemanggilan (fungsi | file | nomor baris)

| Fungsi | File aplikasi | Nomor baris pemanggilan |
|---|---|---|
| `ok` | `perpustakaan.py` | 91, 101, 113, 164 |
| `ok` | `booking.py` | 55, 66, 78, 89 |
| `ok` | `loket.py` | 69, 92 |
| `ok` | `keuangan.py` | 18, 43 |
| `ok` | `todo.py` | 28, 33, 40, 82 |
| `err` | `perpustakaan.py` | 91, 100, 101, 113, 149 |
| `err` | `booking.py` | 56, 66, 75, 77, 89 |
| `err` | `loket.py` | 68, 69, 77 |
| `err` | `keuangan.py` | 18, 42 |
| `err` | `todo.py` | 28, 33, 38, 82 |
| `map_result` | `perpustakaan.py` | 136 |
| `map_result` | `booking.py` | 122, 123 |
| `map_result` | `loket.py` | 95 |
| `map_result` | `keuangan.py` | 60 |
| `map_result` | `todo.py` | 69 |
| `flat_map` | `perpustakaan.py` | 133, 134, 135 |
| `flat_map` | `booking.py` | 118, 119, 120, 121 |
| `flat_map` | `loket.py` | 93, 94 |
| `flat_map` | `keuangan.py` | 59 |
| `flat_map` | `todo.py` | 68 |
| `pipe` | `perpustakaan.py` | 130 |
| `pipe` | `booking.py` | 115 |
| `pipe` | `loket.py` | 91 |
| `pipe` | `keuangan.py` | 56 |
| `pipe` | `todo.py` | 64 |
| `compose` | `perpustakaan.py` | 80 |
| `compose` | `booking.py` | 128 |
| `compose` | `loket.py` | 56 |
| `compose` | `keuangan.py` | 72 |
| `compose` | `todo.py` | 106 |
| `validate` | `perpustakaan.py` | 14 |
| `validate` | `booking.py` | 14 |
| `validate` | `loket.py` | 76 |
| `validate` | `keuangan.py` | 21 |
| `validate` | `todo.py` | 66 |
| `required` | `perpustakaan.py` | 15, 16 |
| `required` | `booking.py` | 15, 16 |
| `required` | `loket.py` | 76 |
| `required` | `keuangan.py` | 22 |
| `required` | `todo.py` | 66 |
| `in_range` | `perpustakaan.py` | 17 |
| `in_range` | `booking.py` | 17, 18 |
| `in_range` | `loket.py` | 76 |
| `in_range` | `keuangan.py` | 23 |
| `min_length` | `perpustakaan.py` | 15 |
| `min_length` | `booking.py` | 15 |
| `min_length` | `keuangan.py` | 23 |
| `min_length` | `todo.py` | 66 |
| `group_by` | `perpustakaan.py` | 76 |
| `group_by` | `booking.py` | 130 |
| `group_by` | `loket.py` | 52, 58 |
| `group_by` | `keuangan.py` | 76, 82 |
| `group_by` | `todo.py` | 102 |
| `sum_by` | `perpustakaan.py` | 81 |
| `sum_by` | `booking.py` | 65, 129 |
| `sum_by` | `loket.py` | 57 |
| `sum_by` | `keuangan.py` | 74, 83, 107 |
| `sum_by` | `todo.py` | 107 |
| `format_rupiah` | `perpustakaan.py` | 155, 191 |
| `format_rupiah` | `booking.py` | 66, 163, 165, 166 |
| `format_rupiah` | `loket.py` | 78, 107, 117, 118 |
| `format_rupiah` | `keuangan.py` | 100, 102, 103, 105, 109, 125 |
| `some` | `perpustakaan.py` | 35, 152 |
| `some` | `booking.py` | 25 |
| `some` | `loket.py` | 23 |
| `some` | `todo.py` | 46 |
| `none` | `perpustakaan.py` | 35, 156 |
| `none` | `booking.py` | 25 |
| `none` | `loket.py` | 23 |
| `none` | `todo.py` | 46 |
| `get_or_else` | `perpustakaan.py` | 90, 98, 147, 178 |
| `get_or_else` | `booking.py` | 73, 152 |
| `get_or_else` | `loket.py` | 28, 66, 120 |
| `get_or_else` | `todo.py` | 81, 136 |
| `diff_days` | `perpustakaan.py` | 142, 150 |
| `diff_days` | `booking.py` | 55 |
| `diff_days` | `todo.py` | 33, 51 |
| `is_overlap` | `perpustakaan.py` | 111 |
| `is_overlap` | `booking.py` | 44, 88 |
| `is_overlap` | `todo.py` | 91 |
| `sort_by` | `perpustakaan.py` | 71 |
| `sort_by` | `booking.py` | 142 |
| `sort_by` | `loket.py` | 47 |
| `sort_by` | `keuangan.py` | 73 |
| `sort_by` | `todo.py` | 96, 118 |
| `top_n` | `perpustakaan.py` | 66 |
| `top_n` | `booking.py` | 137 |
| `top_n` | `keuangan.py` | 95 |
| `where` | `perpustakaan.py` | 34, 56, 61, 109 |
| `where` | `booking.py` | 24, 42, 49, 62, 86 |
| `where` | `loket.py` | 22, 42 |
| `where` | `keuangan.py` | 43, 83, 90, 95 |
| `where` | `todo.py` | 39, 45, 89, 96, 119 |
| `and_` | `perpustakaan.py` | 56, 109 |
| `and_` | `booking.py` | 42, 49, 62, 86 |
| `and_` | `loket.py` | 42 |
| `and_` | `keuangan.py` | 90 |
| `and_` | `todo.py` | 39, 89, 96 |
| `not_` | `perpustakaan.py` | 61 |
| `not_` | `booking.py` | 63 |
| `not_` | `loket.py` | 42 |
| `not_` | `todo.py` | 39, 90, 96 |
| `assoc` | `perpustakaan.py` | 124, 160, 162 |
| `assoc` | `booking.py` | 96 |
| `assoc` | `loket.py` | 85 |
| `assoc` | `todo.py` | 83 |
| `update_where` | `perpustakaan.py` | 122, 159, 161 |
| `update_where` | `booking.py` | 101 |
| `update_where` | `loket.py` | 85 |
| `update_where` | `todo.py` | 83 |

## 5. Instalasi dan Cara Menjalankan

Butuh Python 3.10+. Satu-satunya dependensi adalah `pytest` (untuk pengujian).

```bash
pip install -r requirements.txt

python perpustakaan.py   # demo aplikasi 1
python booking.py        # demo aplikasi 2
python loket.py          # demo aplikasi 3
python keuangan.py       # demo aplikasi 4
python todo.py           # demo aplikasi 5
python main.py           # skenario gabungan 7 langkah
pytest -v                # 54 unit test untuk seluruh 25 fungsi
```

## 6. Anggota Kelompok

| No | Nama | NIM | Tugas |
|----|------|-----|-------|
| 1 | (isi nama) | (isi NIM) | (mis. fplib.py + test) |
| 2 | (isi nama) | (isi NIM) | (mis. Perpustakaan) |
| 3 | (isi nama) | (isi NIM) | (mis. Booking & Loket) |
| 4 | (isi nama) | (isi NIM) | (mis. Keuangan & Todo) |
