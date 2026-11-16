"""data.py - Data contoh (immutable: tuple, frozenset, dict yang tidak dimutasi)."""
from datetime import date, datetime

DENDA_PER_HARI = 2000
KATEGORI_PEMASUKAN = frozenset({"denda", "sewa"})
KATEGORI_PENGELUARAN = frozenset({"beli_buku", "operasional"})
PRIORITAS = ("tinggi", "sedang", "rendah")

ANGGOTA = (
    {"id": "A001", "nama": "Andi"},
    {"id": "A002", "nama": "Budi"},
    {"id": "A003", "nama": "Citra"},
)

BUKU = (
    {"id": "B001", "judul": "Pemrograman Fungsional", "kategori": "Komputer"},
    {"id": "B002", "judul": "Struktur Data", "kategori": "Komputer"},
    {"id": "B003", "judul": "Laskar Pelangi", "kategori": "Novel"},
    {"id": "B004", "judul": "Sejarah Indonesia", "kategori": "Sejarah"},
)

RUANGAN = (
    {"id": "R01", "nama": "Ruang Diskusi A", "tarif_per_jam": 15000},
    {"id": "R02", "nama": "Ruang Diskusi B", "tarif_per_jam": 20000},
)

BOOKING_AWAL = (
    {"id": "B001", "anggota_id": "A002", "ruangan_id": "R01",
     "mulai": datetime(2026, 11, 12, 9), "selesai": datetime(2026, 11, 12, 11),
     "biaya": 30000},
    {"id": "B002", "anggota_id": "A003", "ruangan_id": "R02",
     "mulai": datetime(2026, 11, 10, 13), "selesai": datetime(2026, 11, 10, 16),
     "biaya": 60000},
)

TRANSAKSI_AWAL = (
    {"id": "K001", "tanggal": date(2026, 10, 5), "jenis": "masuk", "kategori": "denda",
     "nominal": 8000, "keterangan": "Denda anggota Oktober"},
    {"id": "K002", "tanggal": date(2026, 10, 12), "jenis": "masuk", "kategori": "sewa",
     "nominal": 45000, "keterangan": "Sewa ruang Oktober"},
    {"id": "K003", "tanggal": date(2026, 10, 20), "jenis": "keluar", "kategori": "beli_buku",
     "nominal": 250000, "keterangan": "Pembelian buku baru"},
    {"id": "K004", "tanggal": date(2026, 11, 2), "jenis": "keluar", "kategori": "operasional",
     "nominal": 120000, "keterangan": "Listrik dan internet"},
    {"id": "K005", "tanggal": date(2026, 11, 9), "jenis": "masuk", "kategori": "sewa",
     "nominal": 60000, "keterangan": "Sewa ruang Citra"},
)

TUGAS_AWAL = (
    {"id": "T001", "judul": "Inventaris rak buku B", "prioritas": "tinggi",
     "mulai": date(2026, 11, 9), "deadline": date(2026, 11, 13),
     "otomatis": False, "selesai": False},
    {"id": "T002", "judul": "Pesan buku baru", "prioritas": "sedang",
     "mulai": date(2026, 11, 10), "deadline": date(2026, 11, 20),
     "otomatis": False, "selesai": False},
    {"id": "T003", "judul": "Rapikan arsip lama", "prioritas": "rendah",
     "mulai": date(2026, 11, 5), "deadline": date(2026, 11, 30),
     "otomatis": False, "selesai": False},
)
