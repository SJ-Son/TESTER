import ast
import logging

logger = logging.getLogger(__name__)


class SecurityChecker(ast.NodeVisitor):
    """AST 기반 정적 분석을 통해 금지된 모듈 및 패턴을 감지하는 보안 검사기.

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
    }

    FORBIDDEN_FUNCTIONS = {"eval", "exec", "open", "compile", "__import__", "input"}

    def __init__(self):
        """SecurityChecker 인스턴스를 초기화합니다."""
        self.errors = []

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
        """함수 호출을 방문하여 금지된 함수인지 확인합니다."""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_FUNCTIONS:
                self.errors.append(f"금지된 함수 호출: {node.func.id}")
        self.generic_visit(node)

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
