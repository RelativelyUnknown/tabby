from cleaner.cli import main


def test_dry_run_keeps_files_and_names_them(tmp_path, capsys):
    f = tmp_path / "a.log"
    f.write_text("x")
    assert main(["--dry-run", str(f)]) == 0
    assert f.exists()
    assert "a.log" in capsys.readouterr().out


def test_without_flag_still_deletes(tmp_path):
    f = tmp_path / "b.log"
    f.write_text("x")
    assert main([str(f)]) == 0
    assert not f.exists()
