from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Optional, Sequence, Set


@dataclass(frozen=True)
class FailureReason:
    code: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location = f" at line {self.line}"
        return f"{self.code}: {self.message}{location}"


@dataclass(frozen=True)
class ValidationConfig:
    allowed_function: str = "score_candidate"
    allowed_imports: Sequence[str] = ()
    allowed_builtins: Sequence[str] = (
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "float",
        "int",
        "len",
        "list",
        "max",
        "min",
        "pow",
        "range",
        "round",
        "set",
        "sorted",
        "sum",
        "tuple",
        "zip",
    )
    extra_allowed_globals: Sequence[str] = ()
    dangerous_calls: Sequence[str] = (
        "__import__",
        "compile",
        "eval",
        "exec",
        "globals",
        "input",
        "locals",
        "open",
        "vars",
    )
    dangerous_names: Sequence[str] = (
        "builtins",
        "ctypes",
        "glob",
        "http",
        "importlib",
        "inspect",
        "multiprocessing",
        "os",
        "pathlib",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "sys",
        "threading",
        "urllib",
    )


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    failure_reason: Optional[FailureReason] = None
    function_name: Optional[str] = None
    referenced_globals: Set[str] = field(default_factory=set)


def validate_candidate_code(
    code: str, config: Optional[ValidationConfig] = None
) -> ValidationResult:
    config = config or ValidationConfig()
    try:
        module = ast.parse(code)
    except SyntaxError as exc:
        return _fail("syntax_error", exc.msg, exc.lineno, exc.offset)

    import_failure = _find_disallowed_import(module, config)
    if import_failure is not None:
        return import_failure

    if len(module.body) != 1:
        return _fail(
            "multiple_top_level_statements",
            "candidate code must contain exactly one top-level function",
        )

    function = module.body[0]
    if isinstance(function, ast.AsyncFunctionDef):
        return _fail(
            "async_function_not_allowed", "async scoring functions are blocked"
        )
    if not isinstance(function, ast.FunctionDef):
        return _fail(
            "missing_allowed_function",
            f"candidate must define {config.allowed_function}",
            getattr(function, "lineno", None),
            getattr(function, "col_offset", None),
        )
    if function.name != config.allowed_function:
        return _fail(
            "missing_allowed_function",
            f"candidate must define {config.allowed_function}",
            function.lineno,
            function.col_offset,
        )
    if function.decorator_list:
        return _fail("decorator_not_allowed", "decorators are blocked")
    if function.args.vararg is not None or function.args.kwarg is not None:
        return _fail(
            "variadic_args_not_allowed",
            "scoring functions must use explicit arguments only",
        )

    nested_function = _find_nested_function(function)
    if nested_function is not None:
        return _fail(
            "nested_function_not_allowed",
            "helper functions are blocked",
            getattr(nested_function, "lineno", None),
            getattr(nested_function, "col_offset", None),
        )

    for node in ast.walk(function):
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            return _fail(
                "global_statement_not_allowed",
                "global and nonlocal statements are blocked",
                node.lineno,
                node.col_offset,
            )
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return _fail(
                "dunder_access",
                "dunder attribute access is blocked",
                node.lineno,
                node.col_offset,
            )

    dangerous_name = _find_dangerous_name(function, config)
    if dangerous_name is not None:
        return dangerous_name

    dangerous_call = _find_dangerous_call(function, config)
    if dangerous_call is not None:
        return dangerous_call

    local_names = _collect_local_names(function)
    referenced_globals = _collect_referenced_globals(function, local_names, config)
    if referenced_globals:
        name = sorted(referenced_globals)[0]
        return _fail("disallowed_global", f"global name {name!r} is not allowed")

    return ValidationResult(
        ok=True, function_name=function.name, referenced_globals=referenced_globals
    )


def _fail(
    code: str,
    message: str,
    line: Optional[int] = None,
    column: Optional[int] = None,
) -> ValidationResult:
    return ValidationResult(
        ok=False,
        failure_reason=FailureReason(
            code=code, message=message, line=line, column=column
        ),
    )


def _find_disallowed_import(
    module: ast.Module, config: ValidationConfig
) -> Optional[ValidationResult]:
    allowed = set(config.allowed_imports)
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in allowed:
                    return _fail(
                        "import_not_allowed",
                        f"import {alias.name!r} is not allowed",
                        node.lineno,
                        node.col_offset,
                    )
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root not in allowed:
                return _fail(
                    "import_not_allowed",
                    f"import from {node.module!r} is not allowed",
                    node.lineno,
                    node.col_offset,
                )
    return None


def _find_nested_function(function: ast.FunctionDef) -> Optional[ast.AST]:
    for node in ast.walk(function):
        if node is function:
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return node
    return None


def _find_dangerous_name(
    function: ast.FunctionDef, config: ValidationConfig
) -> Optional[ValidationResult]:
    dangerous = set(config.dangerous_names)
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id in dangerous
        ):
            return _fail(
                "dangerous_name",
                f"name {node.id!r} is blocked",
                node.lineno,
                node.col_offset,
            )
    return None


def _find_dangerous_call(
    function: ast.FunctionDef, config: ValidationConfig
) -> Optional[ValidationResult]:
    dangerous = set(config.dangerous_calls)
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        call_name = _call_name(node.func)
        if call_name in dangerous:
            return _fail(
                "dangerous_call",
                f"call to {call_name!r} is blocked",
                node.lineno,
                node.col_offset,
            )
    return None


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _collect_local_names(function: ast.FunctionDef) -> Set[str]:
    names = {arg.arg for arg in function.args.args}
    names.update(arg.arg for arg in function.args.kwonlyargs)
    if function.args.vararg is not None:
        names.add(function.args.vararg.arg)
    if function.args.kwarg is not None:
        names.add(function.args.kwarg.arg)
    for node in ast.walk(function):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.comprehension):
            for target in ast.walk(node.target):
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _collect_referenced_globals(
    function: ast.FunctionDef, local_names: Set[str], config: ValidationConfig
) -> Set[str]:
    allowed_globals = set(config.allowed_builtins) | set(config.extra_allowed_globals)
    referenced = set()
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id not in local_names
            and node.id not in allowed_globals
        ):
            referenced.add(node.id)
    return referenced
