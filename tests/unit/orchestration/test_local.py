from quantlab.orchestration.local import build_aider_command


def test_aider_command_is_explicit() -> None:
    cmd = build_aider_command("sonnet", ["src/quantlab/orchestration/contracts.py"])
    assert cmd[:2] == ["aider", "--model"]
    assert "--no-auto-commits" in cmd
    assert cmd[-1].endswith("contracts.py")


def test_aider_command_has_no_shell_interpolation() -> None:
    cmd = build_aider_command("gpt", ["file with spaces.py"])
    assert all("&&" not in part and ";" not in part for part in cmd)
