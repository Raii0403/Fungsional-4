"""Unit test untuk seluruh 25 fungsi di fplib.py. Jalankan: pytest -v"""
from datetime import date, datetime

import fplib

ITEMS = ({"n": "a", "v": 3, "k": "x"}, {"n": "b", "v": 1, "k": "y"}, {"n": "c", "v": 2, "k": "x"})


# ------------------------------------------------------------ 1. Result
def test_ok():
    assert fplib.ok(5) == ("ok", 5)

def test_ok_membungkus_none():
    assert fplib.ok(None) == ("ok", None)

def test_err():
    assert fplib.err("gagal") == ("err", "gagal")

def test_err_tidak_sama_dengan_ok():
    assert fplib.err("x") != fplib.ok("x")

def test_map_result_ok():
    assert fplib.map_result(fplib.ok(2), lambda x: x * 10) == ("ok", 20)

def test_map_result_err_diteruskan():
    assert fplib.map_result(fplib.err("e"), lambda x: x * 10) == ("err", "e")

def test_flat_map_ok():
    assert fplib.flat_map(fplib.ok(4), lambda x: fplib.ok(x + 1)) == ("ok", 5)

def test_flat_map_berhenti_saat_err():
    panggil = []
    hasil = fplib.flat_map(fplib.err("e"), lambda x: panggil.append(x) or fplib.ok(x))
    assert hasil == ("err", "e") and panggil == []

def test_flat_map_fn_bisa_err():
    assert fplib.flat_map(fplib.ok(1), lambda x: fplib.err("tolak")) == ("err", "tolak")


# ---------------------------------------------------------- 2. Komposisi
def test_pipe_urutan_kiri_ke_kanan():
    assert fplib.pipe(3, lambda x: x + 1, lambda x: x * 2) == 8

def test_pipe_tanpa_fungsi():
    assert fplib.pipe(7) == 7

def test_compose_urutan_kanan_ke_kiri():
    assert fplib.compose(lambda x: x + 1, lambda x: x * 2)(3) == 7

def test_compose_tanpa_fungsi_identitas():
    assert fplib.compose()(9) == 9


# ------------------------------------------------------------ 3. Validasi
def test_required_lolos_dan_gagal():
    assert fplib.required("a")({"a": 1}) == ("ok", {"a": 1})
    assert fplib.required("a")({"a": ""})[0] == "err"

def test_required_field_hilang():
    assert fplib.required("a")({})[0] == "err"

def test_in_range_lolos_dan_batas():
    assert fplib.in_range("n", 1, 5)({"n": 5})[0] == "ok"
    assert fplib.in_range("n", 1, 5)({"n": 6})[0] == "err"

def test_in_range_bukan_angka():
    assert fplib.in_range("n", 1, 5)({"n": "3"})[0] == "err"
    assert fplib.in_range("n", 0, 5)({"n": True})[0] == "err"

def test_min_length_lolos_dan_gagal():
    assert fplib.min_length("s", 3)({"s": "abc"})[0] == "ok"
    assert fplib.min_length("s", 3)({"s": "ab"})[0] == "err"

def test_min_length_field_hilang():
    assert fplib.min_length("s", 1)({})[0] == "err"

def test_validate_lolos_semua_rule():
    v = fplib.validate(fplib.required("a"), fplib.in_range("b", 1, 9))
    assert v({"a": "x", "b": 3}) == ("ok", {"a": "x", "b": 3})

def test_validate_gagal_pesan_jelas():
    v = fplib.validate(fplib.required("a"), fplib.in_range("b", 1, 9))
    hasil = v({"a": "x", "b": 99})
    assert hasil[0] == "err" and "b" in hasil[1]

def test_validate_tanpa_rule_selalu_ok():
    assert fplib.validate()({"z": 1}) == ("ok", {"z": 1})


# ----------------------------------------------------------- 4. Agregasi
def test_group_by():
    g = fplib.group_by(ITEMS, lambda i: i["k"])
    assert set(g) == {"x", "y"} and len(g["x"]) == 2 and isinstance(g["x"], tuple)

def test_group_by_kosong():
    assert fplib.group_by((), lambda i: i) == {}

def test_sum_by():
    assert fplib.sum_by(ITEMS, lambda i: i["v"]) == 6

def test_sum_by_kosong():
    assert fplib.sum_by((), lambda i: i) == 0


# ------------------------------------------------------------- 5. Format
def test_format_rupiah_normal():
    assert fplib.format_rupiah(15000) == "Rp15.000"

def test_format_rupiah_nol_dan_jutaan():
    assert fplib.format_rupiah(0) == "Rp0"
    assert fplib.format_rupiah(2500000) == "Rp2.500.000"

def test_format_rupiah_negatif():
    assert fplib.format_rupiah(-5000) == "-Rp5.000"


# ------------------------------------------------------------- 6. Option
def test_some():
    assert fplib.some(1) == ("some", 1)

def test_some_dengan_nol_tetap_some():
    assert fplib.get_or_else(fplib.some(0), 99) == 0

def test_none():
    assert fplib.none() == ("none", None)

def test_none_dua_kali_sama():
    assert fplib.none() == fplib.none()

def test_get_or_else_some():
    assert fplib.get_or_else(fplib.some("a"), "b") == "a"

def test_get_or_else_none():
    assert fplib.get_or_else(fplib.none(), "b") == "b"


# ------------------------------------------------------------ 7. Tanggal
def test_diff_days_positif():
    assert fplib.diff_days(date(2026, 11, 8), date(2026, 11, 11)) == 3

def test_diff_days_negatif_dan_nol():
    assert fplib.diff_days(date(2026, 11, 11), date(2026, 11, 8)) == -3
    assert fplib.diff_days(date(2026, 11, 8), date(2026, 11, 8)) == 0

def test_is_overlap_bentrok():
    assert fplib.is_overlap(datetime(2026, 1, 1, 9), datetime(2026, 1, 1, 11),
                            datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 12))

def test_is_overlap_tidak_bentrok_termasuk_bersinggungan():
    assert not fplib.is_overlap(9, 11, 11, 13)
    assert not fplib.is_overlap(9, 10, 12, 13)


# ------------------------------------------------------- 8. Pengurutan
def test_sort_by_naik_dan_turun():
    assert tuple(map(lambda i: i["n"], fplib.sort_by(ITEMS, lambda i: i["v"]))) == ("b", "c", "a")
    assert tuple(map(lambda i: i["n"], fplib.sort_by(ITEMS, lambda i: i["v"], True))) == ("a", "c", "b")

def test_sort_by_tidak_mengubah_data_asli():
    asli = list(ITEMS)
    salinan = list(asli)
    hasil = fplib.sort_by(asli, lambda i: i["v"])
    assert asli == salinan and isinstance(hasil, tuple)

def test_top_n():
    assert tuple(map(lambda i: i["n"], fplib.top_n(ITEMS, lambda i: i["v"], 2))) == ("a", "c")

def test_top_n_lebih_besar_dari_data_dan_nol():
    assert len(fplib.top_n(ITEMS, lambda i: i["v"], 10)) == 3
    assert fplib.top_n(ITEMS, lambda i: i["v"], 0) == ()


# -------------------------------------------------------- 9. Predikat
def test_where():
    assert len(fplib.where(ITEMS, lambda i: i["k"] == "x")) == 2

def test_where_tidak_ada_yang_lolos():
    assert fplib.where(ITEMS, lambda i: False) == ()

def test_and_semua_harus_benar():
    p = fplib.and_(lambda i: i["k"] == "x", lambda i: i["v"] > 2)
    assert tuple(map(lambda i: i["n"], fplib.where(ITEMS, p))) == ("a",)

def test_and_tanpa_predikat_benar():
    assert fplib.and_()(object()) is True

def test_not_membalik():
    p = fplib.not_(lambda i: i["k"] == "x")
    assert tuple(map(lambda i: i["n"], fplib.where(ITEMS, p))) == ("b",)

def test_not_dua_kali_kembali_semula():
    p = lambda i: i["v"] > 1
    assert fplib.not_(fplib.not_(p))(ITEMS[0]) == p(ITEMS[0])


# ---------------------------------------------------- 10. Immutable
def test_assoc_membuat_dict_baru():
    asli = {"a": 1, "b": 2}
    baru = fplib.assoc(asli, "a", 9)
    assert baru == {"a": 9, "b": 2} and asli == {"a": 1, "b": 2} and baru is not asli

def test_assoc_field_baru():
    assert fplib.assoc({"a": 1}, "z", 0) == {"a": 1, "z": 0}

def test_update_where():
    hasil = fplib.update_where(ITEMS, lambda i: i["k"] == "x", lambda i: fplib.assoc(i, "v", 0))
    assert tuple(map(lambda i: i["v"], hasil)) == (0, 1, 0)

def test_update_where_data_asli_tidak_berubah():
    asli = tuple({**i} for i in ITEMS)
    salinan = tuple({**i} for i in asli)
    fplib.update_where(asli, lambda i: True, lambda i: fplib.assoc(i, "v", 100))
    assert asli == salinan

def test_update_where_tidak_ada_yang_lolos():
    assert fplib.update_where(ITEMS, lambda i: False, lambda i: None) == ITEMS
