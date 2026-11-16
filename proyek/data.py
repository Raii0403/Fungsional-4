"""data.py - Data contoh (immutable: tuple, frozenset, dict yang tidak dimutasi)."""
from datetime import date, datetime

DENDA_PER_HARI = 2000
KATEGORI_KEUANGAN = frozenset({"denda", "sewa", "beli_buku", "operasional"})
KATEGORI_PEMASUKAN = frozenset({"denda", "sewa"})
PRIORITAS = ("tinggi", "sedang", "rendah")

ANGGOTA = (
    {"id": "A001", "nama": "Andi"},
    {"id": "A002", "nama": "Budi"},
    {"id": "A003", "nama": "Citra"},
)

BUKU = (
    {"id": "B001", "judul": "Pemrograman Fungsional", "kategori": "Komputer", "status": "tersedia"},
    {"id": "B002", "judul": "Struktur Data", "kategori": "Komputer", "status": "tersedia"},
    {"id": "B003", "judul": "Laskar Pelangi", "kategori": "Novel", "status": "tersedia"},
    {"id": "B004", "judul": "Sejarah Indonesia", "kategori": "Sejarah", "status": "tersedia"},
    {"id": "B005", "judul": "Bumi Manusia", "kategori": "Novel", "status": "tersedia"},
)

RUANGAN = (
    {"id": "R01", "nama": "Ruang Diskusi A", "tarif_per_jam": 15000},
    {"id": "R02", "nama": "Ruang Diskusi B", "tarif_per_jam": 20000},
)

BOOKING_AWAL = (
    {"id": "BK001", "anggota_id": "A002", "ruangan_id": "R01", "status": "dikonfirmasi",
     "mulai": datetime(2026, 11, 12, 9), "selesai": datetime(2026, 11, 12, 11), "biaya": 30000},
    {"id": "BK002", "anggota_id": "A003", "ruangan_id": "R02", "status": "dikonfirmasi",
     "mulai": datetime(2026, 11, 10, 13), "selesai": datetime(2026, 11, 10, 16), "biaya": 60000},
)

TAGIHAN_AWAL = (
    {"id": "TGH-001", "jenis": "denda", "anggota_id": "A002", "jumlah": 4000,
     "tanggal": date(2026, 11, 5), "lunas": False, "keterangan": "Denda telat 2 hari"},
    {"id": "TGH-002", "jenis": "sewa", "anggota_id": "A003", "jumlah": 60000,
     "tanggal": date(2026, 11, 10), "lunas": True, "keterangan": "Sewa ruang R02"},
    {"id": "TGH-003", "jenis": "sewa", "anggota_id": "A002", "jumlah": 30000,
     "tanggal": date(2026, 11, 12), "lunas": False, "keterangan": "Sewa ruang R01"},
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
    {"id": "T001", "judul": "Inventaris rak buku B", "prioritas": "tinggi", "estimasi_jam": 4,
     "deadline": date(2026, 11, 13), "otomatis": False, "selesai": False},
    {"id": "T002", "judul": "Pesan buku baru", "prioritas": "sedang", "estimasi_jam": 2,
     "deadline": date(2026, 11, 20), "otomatis": False, "selesai": False},
    {"id": "T003", "judul": "Rapikan arsip lama", "prioritas": "rendah", "estimasi_jam": 6,
     "deadline": date(2026, 11, 30), "otomatis": False, "selesai": False},
)
