from analyst import main


def test_main_mencetak_salam(capsys):
    main()
    keluaran = capsys.readouterr().out
    assert "Hello from analyst!" in keluaran
