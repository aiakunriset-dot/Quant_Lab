from quantlab.orchestration.artifacts import sha256_file


def test_sha256_is_deterministic(tmp_path) -> None:
    p = tmp_path / "x.bin"
    p.write_bytes(b"quant-lab")
    assert sha256_file(p) == sha256_file(p)


def test_sha256_changes_with_content(tmp_path) -> None:
    p = tmp_path / "x.bin"
    p.write_bytes(b"a")
    first = sha256_file(p)
    p.write_bytes(b"b")
    assert sha256_file(p) != first
