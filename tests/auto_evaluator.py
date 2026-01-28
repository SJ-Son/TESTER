
import sys
import os
import re
import asyncio
from tenacity import retry, stop_after_attempt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.gemini_service import GeminiService
from src.languages.factory import LanguageFactory

# [Strict Blacklist Validation]
BLACKLIST = {
    "Java": [r"def\s+", r"import\s+pytest", r"console\.log", r"require\(", r"var\s+", r"function\s+"],
    "JavaScript": [r"public\s+class", r"System\.out\.println", r"def\s+", r"import\s+org\.junit"],
    "Python": [r"public\s+class", r"function\s+", r"console\.log", r"var\s+", r"System\.out\.println"]
}

# [Devil's Cases]
TEST_CASES = [
    {
        "id": "TRAP_PY_01",
        "lang": "Python",
        "code": "def calc(a, b):\n    return a + b  # Simple Python"
    },
    {
        "id": "TRAP_JAVA_01", 
        "lang": "Java",
        "code": "public int add(int a, int b) { return a + b; }  # Method only (No class)"
    },
    {
        "id": "TRAP_JS_01",
        "lang": "JavaScript",
        "code": "const sum = (a, b) => a + b;  # Simple JS"
    },
    {
        "id": "TRAP_MIX_01", # JS input but looks like Python
        "lang": "JavaScript",
        "code": "def add(a, b):\n  return a + b" 
        # Expected: Should be handled by Strategy Negative Check or Service Reflection
    }
]

class AutoEvaluator:
    def __init__(self):
        self.service = GeminiService()
        self.results = []

    def check_blacklist(self, code: str, lang: str) -> tuple[bool, str]:
        """블랙리스트 키워드가 있는지 확인"""
        patterns = BLACKLIST.get(lang, [])
        for pattern in patterns:
            if re.search(pattern, code):
                return False, f"Found Forbidden Keyword: '{pattern}'"
        return True, "PASS"

    async def run_single_case(self, case: dict, use_reflection: bool = False):
        print(f"Running {case['id']} ({case['lang']}) [Reflection={use_reflection}]...")
        
        strategy = LanguageFactory.get_strategy(case['lang'])
        
        # 1. Validation Logic Test (Strategy Level)
        # 이미 Strategy에서 Cross-Validation을 하므로, 여기서 먼저 걸러지는지 확인
        valid, msg = strategy.validate_code(case['code'])
        if not valid:
            # 의도된 실패(Trap)인 경우 성공 처리
            if "TRAP_MIX" in case['id']:
                print(f"  -> Caught by Strategy Validation! (Good Detect)")
                return True
            else:
                # 정상 코드인데 실패하면 문제
                print(f"  -> Strategy Validation Failed: {msg}")
                return False

        # 2. Generation Test (Service Level)
        try:
            # stream=True지만 loop를 돌며 전체 텍스트 수집
            generator = self.service.generate_test_code(
                case['code'], 
                system_instruction=strategy.get_system_instruction(),
                stream=True,
                use_reflection=use_reflection
            )
            
            full_code = ""
            for chunk in generator:
                full_code += chunk
            
            # 3. Static Analysis (Blacklist)
            passed, reason = self.check_blacklist(full_code, case['lang'])
            
            if passed:
                print(f"  -> PASS")
                return True
            else:
                print(f"  -> FAIL: {reason}")
                return False
                
        except Exception as e:
            print(f"  -> Error: {e}")
            return False

    async def run_all(self):
        print("=== Auto Evaluator Started ===")
        score = 0
        total = len(TEST_CASES)
        
        for case in TEST_CASES:
            # Reflection 켜고 테스트
            success = await self.run_single_case(case, use_reflection=True)
            if success:
                score += 1
            print("-" * 30)
            
        print(f"Final Score: {score}/{total} ({(score/total)*100:.1f}%)")

if __name__ == "__main__":
    evaluator = AutoEvaluator()
    asyncio.run(evaluator.run_all())
