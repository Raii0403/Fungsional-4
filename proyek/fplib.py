"""fplib.py - Library fungsional: TEPAT 10 fungsi publik, semuanya pure function.

 1. validate       6. sum_by
 2. pipe           7. find_by
 3. where          8. update_where
 4. sort_by        9. format_rupiah
 5. group_by      10. diff_days

Aturan: tanpa print/input, tanpa mengubah argumen, tanpa for/while.
"""
from __future__ import annotations

from datetime import date, datetime
from functools import reduce
from typing import Any, Callable, Iterable, Mapping

Predicate = Callable[[Any], bool]
Rule = tuple  # (predikat, pesan_error)


def validate(data: Mapping[str, Any], rules: Iterable[Rule]) -> list[str]:
    """Kembalikan daftar pesan error dari rule yang gagal; list kosong berarti data valid."""
    return [pesan for predikat, pesan in rules if not predikat(data)]


def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Jalankan fns berurutan dari kiri ke kanan; keluaran satu fungsi menjadi masukan berikutnya."""
    return reduce(lambda acc, fn: fn(acc), fns, value)


def where(items: Iterable[Any], *predicates: Predicate) -> tuple:
    """Tuple baru berisi item yang memenuhi SEMUA predikat."""
    return tuple(filter(lambda x: all(map(lambda p: p(x), predicates)), items))


def sort_by(items: Iterable[Any], key_fn: Callable[[Any], Any], descending: bool = False) -> tuple:
    """Tuple baru yang terurut menurut key_fn; data asli tidak berubah."""
    return tuple(sorted(items, key=key_fn, reverse=descending))


def group_by(items: Iterable[Any], key_fn: Callable[[Any], Any]) -> dict:
    """Kelompokkan items menjadi dict {kunci: tuple item}."""
    return reduce(
        lambda acc, x: {**acc, key_fn(x): acc.get(key_fn(x), ()) + (x,)},
        items,
        {},
    )


def sum_by(items: Iterable[Any], value_fn: Callable[[Any], float]) -> float:
    """Jumlahkan value_fn(item) untuk semua item."""
    return sum(map(value_fn, items))


def find_by(items: Iterable[Any], predicate: Predicate, default: Any = None) -> Any:
    """Item pertama yang cocok dengan predicate, atau default jika tidak ada."""
    return next(filter(predicate, items), default)


def update_where(items: Iterable[Any], predicate: Predicate, changes: Mapping[str, Any]) -> tuple:
    """Tuple baru: item yang lolos predicate digabung dengan changes, lainnya tetap."""
    return tuple(map(lambda x: {**x, **changes} if predicate(x) else x, items))


def format_rupiah(angka: float) -> str:
    """Format angka ke rupiah, contoh 15000 -> 'Rp15.000'."""
    bulat = int(round(angka))
    return ("-" if bulat < 0 else "") + "Rp" + f"{abs(bulat):,}".replace(",", ".")


def diff_days(tanggal_awal: date | datetime, tanggal_akhir: date | datetime) -> int:
    """Selisih hari (akhir - awal); negatif jika akhir sebelum awal."""
    return (tanggal_akhir - tanggal_awal).days
