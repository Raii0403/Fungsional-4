"""Unit test untuk 10 fungsi di fplib.py. Jalankan: pytest -v"""
from datetime import date, datetime

import fplib

ITEMS = ({"n": "a", "v": 3, "k": "x"}, {"n": "b", "v": 1, "k": "y"}, {"n": "c", "v": 2, "k": "x"})
nama = lambda hasil: tuple(map(lambda i: i["n"], hasil))


# ------------------------------------------------------------ validate
def test_validate_lolos_semua_rule():
    rules = [(lambda d: d["a"] != "", "a wajib"), (lambda d: 1 <= d["b"] <= 9, "b harus 1-9")]
    assert fplib.validate({"a": "x", "b": 3}, rules) == []

def test_validate_mengumpulkan_semua_pesan_gagal():
    rules = [(lambda d: d["a"] != "", "a wajib"), (lambda d: 1 <= d["b"] <= 9, "b harus 1-9")]
    assert fplib.validate({"a": "", "b": 99}, rules) == ["a wajib", "b harus 1-9"]

def test_validate_tanpa_rule_valid():
    assert fplib.validate({"a": 1}, []) == []


# ---------------------------------------------------------------- pipe
def test_pipe_urutan_kiri_ke_kanan():
    assert fplib.pipe(3, lambda x: x + 1, lambda x: x * 2) == 8

def test_pipe_tanpa_fungsi_mengembalikan_nilai():
    assert fplib.pipe(7) == 7


# --------------------------------------------------------------- where
def test_where_satu_predikat():
    assert nama(fplib.where(ITEMS, lambda i: i["k"] == "x")) == ("a", "c")

def test_where_banyak_predikat_semua_harus_lolos():
    assert nama(fplib.where(ITEMS, lambda i: i["k"] == "x", lambda i: i["v"] > 2)) == ("a",)

def test_where_tanpa_predikat_atau_tidak_cocok():
    assert fplib.where(ITEMS) == ITEMS
    assert fplib.where(ITEMS, lambda i: False) == ()


# ------------------------------------------------------------- sort_by
def test_sort_by_naik_dan_turun():
    assert nama(fplib.sort_by(ITEMS, lambda i: i["v"])) == ("b", "c", "a")
    assert nama(fplib.sort_by(ITEMS, lambda i: i["v"], descending=True)) == ("a", "c", "b")

def test_sort_by_data_asli_tidak_berubah():
    asli = [{"v": 3}, {"v": 1}, {"v": 2}]
    salinan = [dict(x) for x in asli]
    hasil = fplib.sort_by(asli, lambda i: i["v"])
    assert asli == salinan and isinstance(hasil, tuple) and hasil[0] == {"v": 1}

def test_sort_by_kosong():
    assert fplib.sort_by((), lambda i: i) == ()


# ------------------------------------------------------------ group_by
def test_group_by():
    g = fplib.group_by(ITEMS, lambda i: i["k"])
    assert set(g) == {"x", "y"} and nama(g["x"]) == ("a", "c") and isinstance(g["x"], tuple)

def test_group_by_kosong():
    assert fplib.group_by((), lambda i: i) == {}


# -------------------------------------------------------------- sum_by
def test_sum_by():
    assert fplib.sum_by(ITEMS, lambda i: i["v"]) == 6

def test_sum_by_kosong():
    assert fplib.sum_by((), lambda i: i) == 0


# ------------------------------------------------------------- find_by
def test_find_by_ketemu_mengembalikan_yang_pertama():
    assert fplib.find_by(ITEMS, lambda i: i["k"] == "x")["n"] == "a"

def test_find_by_tidak_ketemu_default():
    assert fplib.find_by(ITEMS, lambda i: i["n"] == "z") is None
    assert fplib.find_by(ITEMS, lambda i: i["n"] == "z", "kosong") == "kosong"


# -------------------------------------------------------- update_where
def test_update_where_menggabungkan_changes():
    hasil = fplib.update_where(ITEMS, lambda i: i["k"] == "x", {"v": 0, "baru": True})
    assert tuple(map(lambda i: i["v"], hasil)) == (0, 1, 0) and hasil[0]["baru"] is True and "baru" not in hasil[1]

def test_update_where_data_asli_tidak_berubah():
    asli = tuple({**i} for i in ITEMS)
    salinan = tuple({**i} for i in asli)
    hasil = fplib.update_where(asli, lambda i: True, {"v": 100})
    assert asli == salinan and hasil is not asli and hasil[0] is not asli[0]

def test_update_where_tidak_ada_yang_lolos():
    assert fplib.update_where(ITEMS, lambda i: False, {"v": 0}) == ITEMS


# ------------------------------------------------------ format_rupiah
def test_format_rupiah_normal():
    assert fplib.format_rupiah(15000) == "Rp15.000"

def test_format_rupiah_nol_dan_jutaan():
    assert fplib.format_rupiah(0) == "Rp0"
    assert fplib.format_rupiah(2500000) == "Rp2.500.000"

def test_format_rupiah_negatif():
    assert fplib.format_rupiah(-5000) == "-Rp5.000"


# ----------------------------------------------------------- diff_days
def test_diff_days_positif():
    assert fplib.diff_days(date(2026, 11, 8), date(2026, 11, 11)) == 3

def test_diff_days_negatif_dan_nol():
    assert fplib.diff_days(date(2026, 11, 11), date(2026, 11, 8)) == -3
    assert fplib.diff_days(date(2026, 11, 8), date(2026, 11, 8)) == 0

def test_diff_days_datetime():
    assert fplib.diff_days(datetime(2026, 1, 1, 23), datetime(2026, 1, 3, 1)) == 1
