from src.languages.java import JavaStrategy
from src.languages.javascript import JavaScriptStrategy
from src.languages.python import PythonStrategy


class TestLanguageStrategies:
    def test_python_strategy_instruction(self):
        strategy = PythonStrategy()
        # get_system_instruction은 인자를 받지 않음
        instruction = strategy.get_system_instruction()

        assert "Google의 전문 QA 엔지니어" in instruction
        assert "pytest" in instruction
        assert "Raw Code" in instruction

    def test_python_strategy_validate(self):
        strategy = PythonStrategy()
        valid, msg = strategy.validate_code("def foo(): pass")
        assert valid is True

        valid, msg = strategy.validate_code("")
        assert valid is False
        assert msg == "코드를 입력해주세요."

    def test_java_strategy_instruction(self):
        strategy = JavaStrategy()
        instruction = strategy.get_system_instruction()

        assert "JUnit 5" in instruction
        assert "Mockito" in instruction

    def test_javascript_strategy_instruction(self):
        strategy = JavaScriptStrategy()
        instruction = strategy.get_system_instruction()

        assert "Jest" in instruction
