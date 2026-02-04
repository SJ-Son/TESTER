import pytest
from src.languages.factory import LanguageFactory
from src.languages.java import JavaStrategy
from src.languages.javascript import JavaScriptStrategy
from src.languages.python import PythonStrategy


class TestLanguageFactory:
    def test_get_strategy_returns_correct_instance(self):
        assert isinstance(LanguageFactory.get_strategy("Python"), PythonStrategy)
        assert isinstance(LanguageFactory.get_strategy("JavaScript"), JavaScriptStrategy)
        assert isinstance(LanguageFactory.get_strategy("Java"), JavaStrategy)

    def test_case_insensitive(self):
        assert isinstance(LanguageFactory.get_strategy("javascript"), JavaScriptStrategy)
        assert isinstance(LanguageFactory.get_strategy("JAVA"), JavaStrategy)

    def test_default_strategy(self):
        # 지원하지 않는 언어는 UnsupportedLanguageError 발생 확인
        from src.languages.factory import UnsupportedLanguageError

        with pytest.raises(UnsupportedLanguageError):
            LanguageFactory.get_strategy("Go")


class TestPythonStrategy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.strategy = PythonStrategy()

    def test_validate_valid_code(self):
        code = "def foo(): pass"
        valid, msg = self.strategy.validate_code(code)
        assert valid is True
        assert msg == ""

    def test_validate_invalid_code(self):
        code = "def foo(:"  # Syntax Error
        valid, msg = self.strategy.validate_code(code)
        assert valid is False
        assert "유효한 파이썬 코드가 아닙니다" in msg


class TestJavaScriptStrategy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.strategy = JavaScriptStrategy()

    def test_validate_valid_code(self):
        code = "const foo = () => {};"
        valid, msg = self.strategy.validate_code(code)
        assert valid is True

    def test_validate_invalid_code(self):
        code = "Just some random text"
        valid, msg = self.strategy.validate_code(code)
        assert valid is False
        assert "유효한 JavaScript 코드가 아닌" in msg


class TestJavaStrategy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.strategy = JavaStrategy()

    def test_validate_valid_code(self):
        code = "public class MyClass {}"
        valid, msg = self.strategy.validate_code(code)
        assert valid is True

    def test_system_instruction_contains_target_keywords(self):
        instruction = self.strategy.get_system_instruction()
        assert "JUnit 5" in instruction
        assert "Raw Code" in instruction
