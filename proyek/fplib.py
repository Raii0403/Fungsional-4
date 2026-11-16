"""fplib.py - Library fungsional: 25 fungsi murni (pure function), 10 kelompok.

Kelompok:
1.  Result    : ok, err, map_result, flat_map
2.  Komposisi : pipe, compose
3.  Validasi  : validate, required, in_range, min_length
4.  Agregasi  : group_by, sum_by
5.  Format    : format_rupiah
6.  Option    : some, none, get_or_else
7.  Tanggal   : diff_days, is_overlap
8.  Pengurutan: sort_by, top_n
9.  Predikat  : where, and_, not_
10. Immutable : assoc, update_where

Aturan: tanpa print/input, tanpa mutasi argumen, tanpa perulangan for/while.
"""
from __future__ import annotations

from datetime import date, datetime
from functools import reduce
from typing import Any, Callable, Iterable, Mapping, Tuple

# Result dan Option direpresentasikan sebagai tuple (tag, nilai) yang immutable.
Result = Tuple[str, Any]   # ("ok", nilai) | ("err", pesan)
Option = Tuple[str, Any]   # ("some", nilai) | ("none", None)
Rule = Callable[[Mapping[str, Any]], Result]
Predicate = Callable[[Any], bool]


# --------------------------------------------------------------- 1. Result
def ok(value: Any) -> Result:
    """Bungkus nilai sukses sebagai Result."""
    return ("ok", value)


def err(message: str) -> Result:
    """Bungkus pesan kesalahan sebagai Result."""
    return ("err", message)


def map_result(result: Result, fn: Callable[[Any], Any]) -> Result:
    """Terapkan fn pada nilai jika ok; jika err, teruskan apa adanya."""
    return ok(fn(result[1])) if result[0] == "ok" else result


def flat_map(result: Result, fn: Callable[[Any], Result]) -> Result:
    """Terapkan fn (yang mengembalikan Result) jika ok; jika err, hentikan rantai."""
    return fn(result[1]) if result[0] == "ok" else result


# ------------------------------------------------------- 2. pipe & compose
def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Alirkan value melalui fns dari kiri ke kanan."""
    return reduce(lambda acc, fn: fn(acc), fns, value)


def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Gabungkan fns menjadi satu fungsi; urutan eksekusi dari kanan ke kiri."""
    return lambda x: reduce(lambda acc, fn: fn(acc), reversed(fns), x)


# ------------------------------------------------------------ 3. validate
def required(field: str) -> Rule:
    """Rule: field harus ada dan tidak kosong."""
    return lambda data: (
        ok(data) if data.get(field) not in (None, "", ())
        else err(f"Field '{field}' wajib diisi")
    )


def in_range(field: str, minimum: float, maximum: float) -> Rule:
    """Rule: field berupa angka dalam rentang [minimum, maximum]."""
    pesan = (f"Field '{field}' harus bernilai {minimum}" if minimum == maximum
             else f"Field '{field}' harus antara {minimum} dan {maximum}")
    return lambda data: (
        ok(data)
        if isinstance(data.get(field), (int, float))
        and not isinstance(data.get(field), bool)
        and minimum <= data[field] <= maximum
        else err(pesan)
    )


def min_length(field: str, n: int) -> Rule:
    """Rule: panjang teks field minimal n karakter."""
    return lambda data: (
        ok(data) if len(str(data.get(field) or "")) >= n
        else err(f"Field '{field}' minimal {n} karakter")
    )


def validate(*rules: Rule) -> Callable[[Mapping[str, Any]], Result]:
    """Buat validator: ok(data) jika semua rule lolos, err(pesan pertama) jika ada yang gagal."""
    return lambda data: reduce(lambda acc, rule: flat_map(acc, rule), rules, ok(data))


# --------------------------------------------------- 4. group_by & sum_by
def group_by(items: Iterable[Any], key_fn: Callable[[Any], Any]) -> dict:
    """Kelompokkan items menurut key_fn; hasilnya dict baru berisi tuple."""
    return reduce(
        lambda acc, x: {**acc, key_fn(x): acc.get(key_fn(x), ()) + (x,)},
        items,
        {},
    )


def sum_by(items: Iterable[Any], value_fn: Callable[[Any], float]) -> float:
    """Jumlahkan value_fn(x) untuk semua x di items."""
    return sum(map(value_fn, items))


# ------------------------------------------------------- 5. format_rupiah
def format_rupiah(angka: float) -> str:
    """Format angka ke rupiah, contoh 15000 -> 'Rp15.000'."""
    bulat = int(round(angka))
    return ("-" if bulat < 0 else "") + "Rp" + f"{abs(bulat):,}".replace(",", ".")


# ------------------------------------------------------------- 6. Option
def some(value: Any) -> Option:
    """Option berisi nilai."""
    return ("some", value)


def none() -> Option:
    """Option kosong."""
    return ("none", None)


def get_or_else(option: Option, default: Any) -> Any:
    """Ambil nilai Option, atau default jika kosong."""
    return option[1] if option[0] == "some" else default


# ------------------------------------------------------------- 7. tanggal
def diff_days(tanggal_awal: date | datetime, tanggal_akhir: date | datetime) -> int:
    """Selisih hari (akhir - awal); negatif jika akhir sebelum awal."""
    return (tanggal_akhir - tanggal_awal).days


def is_overlap(mulai1: Any, selesai1: Any, mulai2: Any, selesai2: Any) -> bool:
    """True jika rentang [mulai1, selesai1) beririsan dengan [mulai2, selesai2)."""
    return mulai1 < selesai2 and mulai2 < selesai1


# ------------------------------------------------- 8. pengurutan & peringkat
def sort_by(items: Iterable[Any], key_fn: Callable[[Any], Any], descending: bool = False) -> tuple:
    """Urutkan items menurut key_fn; hasilnya tuple baru, data asli tidak berubah."""
    return tuple(sorted(items, key=key_fn, reverse=descending))


def top_n(items: Iterable[Any], key_fn: Callable[[Any], Any], n: int) -> tuple:
    """Ambil n item dengan nilai key_fn terbesar (tuple baru); n > jumlah data aman."""
    return sort_by(items, key_fn, True)[:max(0, n)]


# ------------------------------------------------- 9. penyaringan predikat
def where(items: Iterable[Any], predicate: Predicate) -> tuple:
    """Saring items yang memenuhi predicate; hasilnya tuple baru."""
    return tuple(filter(predicate, items))


def and_(*predicates: Predicate) -> Predicate:
    """Gabungkan predikat dengan DAN: lolos jika semua predikat bernilai True."""
    return lambda x: all(map(lambda p: p(x), predicates))


def not_(predicate: Predicate) -> Predicate:
    """Negasi predikat: lolos jika predicate bernilai False."""
    return lambda x: not predicate(x)


# --------------------------------------------- 10. pembaruan data immutable
def assoc(record: Mapping[str, Any], key: str, value: Any) -> dict:
    """Salin record menjadi dict BARU dengan satu field diubah/ditambah."""
    return {**record, key: value}


def update_where(items: Iterable[Any], predicate: Predicate, updater: Callable[[Any], Any]) -> tuple:
    """Tuple baru: item yang lolos predicate diubah updater, sisanya tetap."""
    return tuple(map(lambda x: updater(x) if predicate(x) else x, items))
