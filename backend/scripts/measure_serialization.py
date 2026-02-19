import json
import random
import string
import time
from typing import Any, Dict, Union

# orjson은 선택적 의존성입니다.
try:
    import orjson
except ImportError:
    orjson = None  # type: ignore


def generate_large_data(depth: int = 3, width: int = 5) -> Union[Dict[str, Any], str]:
    """API 응답을 시뮬레이션하기 위해 대용량 중첩 딕셔너리를 생성합니다.

    재귀적으로 호출되어 지정된 깊이와 너비를 가진 데이터를 생성합니다.

    Args:
        depth (int): 생성할 데이터의 중첩 깊이. 기본값은 3입니다.
        width (int): 각 레벨에서 생성할 키의 개수. 기본값은 5입니다.

    Returns:
        Union[Dict[str, Any], str]: 생성된 중첩 딕셔너리 또는 문자열(리프 노드).
    """
    if depth == 0:
        return "".join(random.choices(string.ascii_letters, k=50))

    return {f"key_{i}": generate_large_data(depth - 1, width) for i in range(width)}


def measure_json() -> float:
    """Python 표준 json 라이브러리의 직렬화 성능을 측정합니다.

    Returns:
        float: 100회 반복 실행 시 평균 직렬화 시간(초).
    """
    data = generate_large_data(depth=4, width=10)

    start_time = time.time()
    iterations = 100
    for _ in range(iterations):
        json.dumps(data)
    end_time = time.time()

    avg_time = (end_time - start_time) / iterations
    print(f"Standard json: {avg_time:.6f} seconds per dump (avg of {iterations})")
    return avg_time


def measure_orjson() -> Union[float, None]:
    """orjson 라이브러리의 직렬화 성능을 측정합니다 (설치된 경우).

    Returns:
        Union[float, None]: 100회 반복 실행 시 평균 직렬화 시간(초).
            orjson이 설치되지 않은 경우 None을 반환합니다.
    """
    if orjson is None:
        print("orjson not installed. Skipping.")
        return None

    data = generate_large_data(depth=4, width=10)

    start_time = time.time()
    iterations = 100
    for _ in range(iterations):
        orjson.dumps(data)
    end_time = time.time()

    avg_time = (end_time - start_time) / iterations
    print(f"orjson:       {avg_time:.6f} seconds per dump (avg of {iterations})")
    return avg_time


if __name__ == "__main__":
    print("Generating data and starting benchmark...")
    baseline = measure_json()
    optimized = measure_orjson()

    if optimized:
        improvement = baseline / optimized
        print(f"Speedup: {improvement:.2f}x")
