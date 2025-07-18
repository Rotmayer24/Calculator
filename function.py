import re
import math
from fractions import Fraction


def calculate_expression(expr: str) -> float:
    """
    Вычисляет арифметическое выражение, переданное строкой.
    Поддерживаются операции +, -, *, /, %, скобки, десятичные числа, sqrt, pow, sin, cos, tan, log, exp, pi, e, Fraction.
    """
    allowed = re.compile(r'^[\d\.\+\-\*/%\(\)\, a-zA-Z_]+$')
    if not allowed.match(expr):
        raise ValueError("Недопустимые символы в выражении")
    expr = expr.replace('%', '/100')
    # Поддержка pow(x, y) через ^ заменяется на ** в main.py
    try:
        result = eval(expr, {
            "__builtins__": None,
            "sqrt": math.sqrt,
            "pow": pow,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "Fraction": Fraction
        }, {})
    except Exception as e:
        raise ValueError(f"Ошибка вычисления: {e}")
    return result

