"""Kontrak sumber data.

Agent hanya mengenal kontrak ini, tidak peduli database apa yang ada di baliknya.
Kalau suatu hari agent perlu tahu engine apa yang dipakai, kontrak inilah yang salah.
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class Kolom:
    nama: str
    tipe: str
    nullable: bool = True


@dataclass(frozen=True)
class TabelSkema:
    nama: str
    kolom: tuple[Kolom, ...]

    def nama_kolom(self) -> list[str]:
        return [k.nama for k in self.kolom]


@dataclass(frozen=True)
class Skema:
    tabel: tuple[TabelSkema, ...]

    def nama_tabel(self) -> list[str]:
        return [t.nama for t in self.tabel]

    def cari(self, nama: str) -> TabelSkema | None:
        for t in self.tabel:
            if t.nama == nama:
                return t
        return None


@dataclass(frozen=True)
class Tabel:
    """Hasil eksekusi sebuah kueri."""

    kolom: tuple[str, ...]
    baris: tuple[tuple[Any, ...], ...]

    @property
    def jumlah_baris(self) -> int:
        return len(self.baris)


@runtime_checkable
class SumberData(Protocol):
    def dialek(self) -> str:
        """Jenis bahasa kueri, misalnya "sql:postgres" atau "sql:mysql"."""
        ...

    def skema(self) -> Skema:
        """Daftar tabel dan kolom yang tersedia."""
        ...

    def kemampuan(self) -> set[str]:
        """Kemampuan sumber, misalnya {"agregasi", "join", "rentang_waktu", "top_n"}."""
        ...

    def jalankan(self, kueri: str) -> Tabel:
        """Jalankan kueri, kembalikan hasilnya."""
        ...
