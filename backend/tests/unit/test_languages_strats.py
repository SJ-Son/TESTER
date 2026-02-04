from src.languages.java import JavaStrategy
from src.languages.javascript import JavaScriptStrategy
from src.languages.python import PythonStrategy


class TestLanguageStrategies:
    def test_python_strategy_prompt(self):
        strategy = PythonStrategy()
        code = "def add(a, b): return a + b"
        prompt = strategy.generate_prompt(code)

        assert "pytest" in prompt
        assert "Unittest" in prompt
        assert code in prompt

    def test_python_strategy_validate(self):
        strategy = PythonStrategy()
        assert strategy.validate("def foo(): pass") is True
        # Simple validation just checks non-empty usually, or basic syntax if implemented.
        # Based on current implementation (likely abstract base check or specific)
        assert strategy.validate("") is False

    def test_java_strategy_prompt(self):
        strategy = JavaStrategy()
        code = "public class Foo {}"
        prompt = strategy.generate_prompt(code)

        assert "JUnit" in prompt
        assert "AssertJ" in prompt or "assertions" in prompt.lower()
        assert code in prompt

    def test_java_strategy_file_extension(self):
        strategy = JavaStrategy()
        assert strategy.get_file_extension() == "java"

    def test_javascript_strategy_prompt(self):
        strategy = JavaScriptStrategy()
        code = "function foo() {}"
        prompt = strategy.generate_prompt(code)

        assert "Jest" in prompt or "Vitest" in prompt
        assert code in prompt

    def test_response_parsing_markdown_removal(self):
        """Test that code blocks are correctly extracted from LLM response"""
        # All strategies likely inherit from BaseLanguageStrategy which handles this,
        # or implement it themselves. We test one representative.
        strategy = PythonStrategy()

        raw_response = """
Here is the code:
```python
def test_foo():
    assert True
```
Hope it helps.
"""
        parsed = strategy.parse_response(raw_response)
        assert "def test_foo():" in parsed
        assert "Here is the code" not in parsed
        assert "```" not in parsed

    def test_response_parsing_no_markdown(self):
        strategy = PythonStrategy()
        raw_code = "def test_foo():\n    assert True"
        parsed = strategy.parse_response(raw_code)
        assert parsed == raw_code
