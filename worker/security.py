import ast
import logging

logger = logging.getLogger(__name__)


class SecurityChecker(ast.NodeVisitor):
    """
    AST 기반 정적 분석을 통해 금지된 모듈 및 패턴 감지.
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
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split(".")[0] in self.FORBIDDEN_MODULES:
                self.errors.append(f"금지된 모듈 임포트: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split(".")[0] in self.FORBIDDEN_MODULES:
            self.errors.append(f"금지된 모듈에서 임포트: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_FUNCTIONS:
                self.errors.append(f"금지된 함수 호출: {node.func.id}")
        self.generic_visit(node)

    def check_code(self, code: str):
        """
        코드를 파싱하고 보안 위반 사항을 검사합니다.
        잠재적 위협이 발견되면 SecurityViolation을 발생시킵니다.
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
