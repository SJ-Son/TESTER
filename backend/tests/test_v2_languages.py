
import pytest
from src.languages.factory import LanguageFactory
from src.languages.python import PythonStrategy
from src.languages.javascript import JavaScriptStrategy
from src.languages.java import JavaStrategy

class TestLanguageFactory:
    def test_get_strategy_returns_correct_instance(self):
        assert isinstance(LanguageFactory.get_strategy("Python"), PythonStrategy)
        assert isinstance(LanguageFactory.get_strategy("JavaScript"), JavaScriptStrategy)
        assert isinstance(LanguageFactory.get_strategy("Java"), JavaStrategy)
        
    def test_case_insensitive(self):
        assert isinstance(LanguageFactory.get_strategy("javascript"), JavaScriptStrategy)
        assert isinstance(LanguageFactory.get_strategy("JAVA"), JavaStrategy)

    def test_default_strategy(self):
        # 지원하지 않는 언어는 PythonStrategy 반환
        assert isinstance(LanguageFactory.get_strategy("Go"), PythonStrategy)

class TestPythonStrategy:
    def setup_method(self):
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

    def test_streamlit_language(self):
        assert self.strategy.get_streamlit_language() == "python"

class TestJavaScriptStrategy:
    def setup_method(self):
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

    def test_negative_check_python(self):
        # 파이썬 코드를 넣었을 때 실패해야 함
        code = "def hello():\n    return 'Hello'"
        valid, msg = self.strategy.validate_code(code)
        assert valid is False
        assert "Python 코드로 감지" in msg

    def test_negative_check_java(self):
        # 자바 코드를 넣었을 때 실패해야 함
        code = "public static void main(String[] args) {}"
        valid, msg = self.strategy.validate_code(code)
        assert valid is False
        assert "Java 코드로 감지" in msg

    def test_placeholder(self):
        assert "const" in self.strategy.get_placeholder()
    
    def test_prompt_consistency(self):
        instr = self.strategy.get_system_instruction()
        assert "모듈 시스템 일관성" in instr
        assert "require" in instr

class TestJavaStrategy:
    def setup_method(self):
        self.strategy = JavaStrategy()

    def test_validate_valid_code(self):
        code = "public class MyClass {}"
        valid, msg = self.strategy.validate_code(code)
        assert valid is True

    def test_validate_invalid_code_python(self):
        code = "def foo(): pass"  # Python code
        valid, msg = self.strategy.validate_code(code)
        assert valid is False
        assert "Python 코드로 감지" in msg

    def test_validate_invalid_code_js(self):
        code = "console.log('hello');"
        valid, msg = self.strategy.validate_code(code)
        assert valid is False
        assert "JavaScript 코드로 감지" in msg
        
    def test_system_instruction_contains_import_rule(self):
        instruction = self.strategy.get_system_instruction()
        assert "반드시 필요한 모든 라이브러리" in instruction
        assert "Import 구문을 코드 상단에 포함" in instruction
        assert "Class Wrapper" in instruction
        assert "package" in instruction
