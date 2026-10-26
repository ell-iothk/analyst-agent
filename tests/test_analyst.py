from analyst import main


def test_main_prints_greeting(capsys):
    main()
    output = capsys.readouterr().out
    assert "Hello from analyst!" in output
