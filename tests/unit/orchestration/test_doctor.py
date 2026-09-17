from quantlab.orchestration.doctor import check_project_root


def test_project_root_check_uses_case_insensitive_windows_name() -> None:
    assert check_project_root("C:/QUANT_LAB") is True
    assert check_project_root("C:/quant_lab") is True
    assert check_project_root("C:/OTHER") is False
