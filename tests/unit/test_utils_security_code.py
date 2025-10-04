from core.utils import normalize_security_code


def test_normalize_security_code_basic():
    assert normalize_security_code("7203") == "7203"
    assert normalize_security_code(8035) == "8035"


def test_normalize_security_code_strip_non_digits_and_left_pad():
    assert normalize_security_code("  235 ") == "0235"
    assert normalize_security_code("A12B3") == "A12B3"


def test_normalize_security_code_cut_extra_digits():
    # 末尾に余計な桁がある場合は先頭4桁のみ採用（下1桁0埋めを防止）
    assert normalize_security_code("72030") == "7203"
    assert normalize_security_code("007203") == "7203"


def test_normalize_security_code_empty():
    assert normalize_security_code("") == "0000"
    assert normalize_security_code(None) == "0000"
