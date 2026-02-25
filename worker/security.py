import ast
import logging

logger = logging.getLogger(__name__)


class SecurityChecker(ast.NodeVisitor):
    """AST 기반 정적 분석을 통해 금지된 모듈 및 패턴을 감지하는 보안 검사기.

    단순 키워드 매칭을 넘어 동적 우회 패턴(문자열 연결, getattr, __builtins__ 접근 등)
    까지 탐지합니다.

    Attributes:
        errors: 감지된 보안 위반 사항 목록.
    """

    FORBIDDEN_MODULES = {
        "os",
        "subprocess",
        "shutil",
        "sys",
        "importlib",
        "socket",
        "urllib",
        "requests",
        "http",
        "ftplib",
        "telnetlib",
        "pickle",
        "marshal",
        "builtins",
        "ctypes",  # 네이티브 코드 접근
        "cffi",  # C 함수 인터페이스
        "signal",  # 프로세스 시그널 조작
        "resource",  # 리소스 제한 변경
        "pty",  # 의사 터미널 생성
        "multiprocessing",
        "threading",  # 스레드 기반 탈출 방지
        "concurrent",
        "asyncio",  # 이벤트 루프 조작 방지
    }

    FORBIDDEN_FUNCTIONS = {
        "eval",
        "exec",
        "open",
        "compile",
        "__import__",
        "input",
        "getattr",
        "setattr",  # 동적 속성 설정으로 우회 가능
        "delattr",
        "vars",  # 객체 내부 딕셔너리 접근
        "dir",  # 속성 목록 열거 (정찰용)
        "globals",  # 전역 네임스페이스 노출
        "locals",  # 지역 네임스페이스 노출
        "breakpoint",  # 디버거 호출
        "memoryview",  # 메모리 직접 접근
    }

    FORBIDDEN_ATTRIBUTES = {
        "__subclasses__",
        "__bases__",
        "__globals__",
        "__builtins__",
        "__closure__",
        "__code__",
        "__mro__",
        "__module__",
        "__loader__",
        "__spec__",
        "__file__",  # 파일 경로 노출
        "__dict__",  # 내부 딕셔너리 접근
        "func_globals",  # Python 2 잔재 우회
        "gi_frame",  # 제너레이터 프레임 접근
    }

    def __init__(self):
        """SecurityChecker 인스턴스를 초기화합니다."""
        self.errors = []

    def visit_Attribute(self, node):
        """속성 접근을 방문하여 금지된 속성인지 확인합니다."""
        if node.attr in self.FORBIDDEN_ATTRIBUTES:
            self.errors.append(f"금지된 속성 접근: {node.attr}")
        self.generic_visit(node)

    def visit_Import(self, node):
        """import 구문을 방문하여 금지된 모듈인지 확인합니다."""
        for alias in node.names:
            if alias.name.split(".")[0] in self.FORBIDDEN_MODULES:
                self.errors.append(f"금지된 모듈 임포트: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """from ... import 구문을 방문하여 금지된 모듈인지 확인합니다."""
        if node.module and node.module.split(".")[0] in self.FORBIDDEN_MODULES:
            self.errors.append(f"금지된 모듈에서 임포트: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        """함수 호출을 방문하여 금지된 함수인지 확인합니다.

        단순 이름 호출뿐 아니라 getattr을 통한 동적 호출 패턴도 감지합니다.
        예: getattr(obj, 'ev'+'al')(), getattr(__builtins__, 'exec')()
        """
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_FUNCTIONS:
                self.errors.append(f"금지된 함수 호출: {node.func.id}")

        # getattr(x, "eval") 형태의 동적 속성 접근 우회 탐지
        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 2:
                second_arg = node.args[1]
                # getattr(obj, "eval") 또는 getattr(obj, 'ev'+'al') 등
                resolved = self._resolve_string_const(second_arg)
                if resolved:
                    if resolved in self.FORBIDDEN_FUNCTIONS:
                        self.errors.append(f"getattr을 통한 금지된 함수 동적 호출 시도: {resolved}")
                    elif resolved in self.FORBIDDEN_ATTRIBUTES:
                        self.errors.append(f"getattr을 통한 금지된 속성 접근 시도: {resolved}")

        self.generic_visit(node)

    def visit_Subscript(self, node):
        """딕셔너리 구독 접근으로 __builtins__['exec'] 형태의 우회를 탐지합니다."""
        if isinstance(node.value, ast.Attribute):
            if node.value.attr in self.FORBIDDEN_ATTRIBUTES:
                self.errors.append(f"금지된 속성의 구독 접근: {node.value.attr}[...]")

        # __builtins__["exec"] 형태
        if isinstance(node.value, ast.Name) and node.value.id == "__builtins__":
            resolved = self._resolve_string_const(node.slice)
            if resolved and resolved in self.FORBIDDEN_FUNCTIONS:
                self.errors.append(f"__builtins__ 구독을 통한 금지된 함수 접근: {resolved}")

        self.generic_visit(node)

    def _resolve_string_const(self, node: ast.expr) -> str | None:
        """AST 노드에서 문자열 상수 값을 추출합니다.

        단순 문자열 상수("eval")와 문자열 연결('ev'+'al') 패턴을 지원합니다.

        Args:
            node: 분석할 AST 표현식 노드.

        Returns:
            추출된 문자열 또는 분석 불가 시 None.
        """
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value

        # 'ev' + 'al' 형태의 문자열 연결
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._resolve_string_const(node.left)
            right = self._resolve_string_const(node.right)
            if left is not None and right is not None:
                return left + right

        return None

    def check_code(self, code: str):
        """코드를 파싱하고 보안 위반 사항을 검사합니다.

        Args:
            code: 검사할 Python 소스 코드.

        Raises:
            SecurityViolation: 잠재적 위협이 발견된 경우.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # 문법 오류는 보안 관점에서는 안전함 (실행되지 않으므로).
            # 실행기(Runner)가 유효한 문법 오류를 보고하도록 둡니다.
            return

        self.visit(tree)

        if self.errors:
            error_msg = "; ".join(self.errors)
            logger.warning(f"보안 검사 실패: {error_msg}")
            raise SecurityViolation(f"보안 위반이 감지되었습니다: {error_msg}")


class SecurityViolation(Exception):
    pass
