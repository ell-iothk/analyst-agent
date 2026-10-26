from analyst.sumber.protokol import Kolom, Skema, SumberData, Tabel, TabelSkema


class SumberPalsu:
    """Sumber data tiruan di memori. Hanya untuk test, tanpa database sungguhan."""

    def dialek(self) -> str:
        return "sql:palsu"

    def skema(self) -> Skema:
        produk = TabelSkema(
            nama="produk",
            kolom=(Kolom("id", "INTEGER", nullable=False), Kolom("nama", "TEXT")),
        )
        return Skema(tabel=(produk,))

    def kemampuan(self) -> set[str]:
        return {"agregasi"}

    def jalankan(self, kueri: str) -> Tabel:
        return Tabel(kolom=("jumlah",), baris=((42,),))


class SumberSetengahJadi:
    """Lupa mengimplementasikan tiga method. Seharusnya tidak dianggap SumberData."""

    def dialek(self) -> str:
        return "sql:rusak"


def test_sumber_lengkap_memenuhi_kontrak():
    assert isinstance(SumberPalsu(), SumberData)


def test_sumber_tidak_lengkap_ditolak():
    assert not isinstance(SumberSetengahJadi(), SumberData)


def test_skema_bisa_ditelusuri():
    skema = SumberPalsu().skema()
    assert skema.nama_tabel() == ["produk"]
    assert skema.cari("produk").nama_kolom() == ["id", "nama"]
    assert skema.cari("tidak_ada") is None


def test_tabel_menghitung_jumlah_baris():
    hasil = SumberPalsu().jalankan("SELECT 42")
    assert hasil.jumlah_baris == 1
    assert hasil.baris[0][0] == 42
