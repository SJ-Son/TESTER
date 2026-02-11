import ast
import logging

logger = logging.getLogger(__name__)


class SecurityChecker(ast.NodeVisitor):
    """
    AST-based static analysis to detect forbidden modules and patterns.
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
                self.errors.append(f"Forbidden import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split(".")[0] in self.FORBIDDEN_MODULES:
            self.errors.append(f"Forbidden import from: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_FUNCTIONS:
                self.errors.append(f"Forbidden function call: {node.func.id}")
        self.generic_visit(node)

    def check_code(self, code: str):
        """
        Parses and checks the code for security violations.
        Raises SecurityViolation if potential threats are found.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Syntax errors are safe from a security perspective (code won't run),
            # but we should let the runner handle reporting valid syntax errors.
            return

        self.visit(tree)

        if self.errors:
            error_msg = "; ".join(self.errors)
            logger.warning(f"Security check failed: {error_msg}")
            raise SecurityViolation(f"Security violation detected: {error_msg}")


class SecurityViolation(Exception):
    pass
