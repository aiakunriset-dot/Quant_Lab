from quantlab.orchestration.handoff import build_colab_manifest


def test_colab_manifest_has_reproducibility_fields() -> None:
    manifest = build_colab_manifest(
        task_id="t1",
        git_revision="abc123",
        datasets=["dataset-a"],
        config_sha256="0" * 64,
        seed=42,
    )
    assert manifest["git_revision"] == "abc123"
    assert manifest["datasets"] == ["dataset-a"]
    assert manifest["seed"] == 42
    assert len(manifest["manifest_sha256"]) == 64


def test_manifest_hash_is_deterministic() -> None:
    a = build_colab_manifest("t1", "abc123", ["a"], "1" * 64, 42)
    b = build_colab_manifest("t1", "abc123", ["a"], "1" * 64, 42)
    assert a["manifest_sha256"] == b["manifest_sha256"]
