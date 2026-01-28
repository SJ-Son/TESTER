
import sys
import os
import asyncio
import time
from tenacity import retry, stop_after_attempt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.gemini_service import GeminiService
from src.languages.factory import LanguageFactory

# [The Trap: Incomplete Java Code]
TRAP_CODE = "public int calculate(int a, int b) { return a + b; }"
LANGUAGE = "Java"

class ReflectionVerifier:
    def __init__(self):
        self.service = GeminiService()
        self.strategy = LanguageFactory.get_strategy(LANGUAGE)

    async def generate(self, reflection: bool) -> str:
        print(f"  > Generating with Reflection={reflection}...")
        start_time = time.time()
        
        # stream=True loop to capture full output
        generator = self.service.generate_test_code(
            TRAP_CODE, 
            system_instruction=self.strategy.get_system_instruction(),
            stream=True,
            use_reflection=reflection
        )
        
        full_code = ""
        for chunk in generator:
            full_code += chunk
            
        elapsed = time.time() - start_time
        print(f"    - Done in {elapsed:.2f}s")
        return full_code

    def analyze(self, code: str) -> dict:
        return {
            "has_class": "class" in code,
            "has_import": "import " in code,
            "has_test_annotation": "@Test" in code,
            "length": len(code)
        }

    async def run_comparison(self):
        print("=== Reflection Effect Verification (A/B Test) ===")
        print(f"Input Code: {TRAP_CODE}")
        print("-" * 40)

        # 1. Case A: No Reflection
        print("[Case A] Reflection: OFF")
        code_a = await self.generate(reflection=False)
        stats_a = self.analyze(code_a)
        
        # 2. Case B: With Reflection
        print("\n[Case B] Reflection: ON")
        code_b = await self.generate(reflection=True)
        stats_b = self.analyze(code_b)

        # 3. Compare
        print("\n=== Results Comparison ===")
        print(f"{'Metric':<20} | {'Case A (OFF)':<15} | {'Case B (ON)':<15}")
        print("-" * 56)
        print(f"{'Has Class Wrapper':<20} | {str(stats_a['has_class']):<15} | {str(stats_b['has_class']):<15}")
        print(f"{'Has Imports':<20} | {str(stats_a['has_import']):<15} | {str(stats_b['has_import']):<15}")
        print(f"{'Has @Test':<20} | {str(stats_a['has_test_annotation']):<15} | {str(stats_b['has_test_annotation']):<15}")
        print(f"{'Code Length':<20} | {str(stats_a['length']):<15} | {str(stats_b['length']):<15}")
        
        print("-" * 56)
        
        # Verdict using heuristic: Case B should be longer and have all True, while Case A might fail some
        # Note: If Case A is surprisingly good, that's also fine, but usually B should be robust.
        
        improved = (not stats_a['has_class'] and stats_b['has_class']) or \
                   (not stats_a['has_import'] and stats_b['has_import']) or \
                   (len(code_b) > len(code_a) + 50) # Rough heuristic for "more complete"

        if improved:
            print("✅ 개선됨 (Improved): Self-Correction verified!")
        elif stats_a['has_class'] and stats_b['has_class']:
            print("❌ 차이 없음 (No Difference): Base model was already good enough.")
        else:
            print("❓ 분석 필요 (Inconclusive)")

if __name__ == "__main__":
    verifier = ReflectionVerifier()
    asyncio.run(verifier.run_comparison())
