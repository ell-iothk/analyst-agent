from analyst.data import download


def test_url_is_pinned_to_a_commit():
    assert download.COMMIT in download.BASE_URL
    assert "/main/" not in download.BASE_URL


def test_existing_file_is_not_downloaded_again(tmp_path, monkeypatch):
    (tmp_path / "sample.csv.gz").write_text("already here")

    def must_not_be_called(*args):
        raise AssertionError("should not download")

    monkeypatch.setattr(download.urllib.request, "urlretrieve", must_not_be_called)
    download.download("sample.csv.gz", tmp_path)


def test_finished_download_leaves_no_part_file(tmp_path, monkeypatch):
    def fake_urlretrieve(url, target):
        target.write_text("fake content")

    monkeypatch.setattr(download.urllib.request, "urlretrieve", fake_urlretrieve)
    result = download.download("sample.csv.gz", tmp_path)

    assert result.read_text() == "fake content"
    assert not (tmp_path / "sample.csv.gz.part").exists()
