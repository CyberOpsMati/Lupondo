import math
import pytest
from src.calculator import (
    add,
    subtract,
    multiply,
    divide,
    power,
    square_root,
    modulo,
    evaluate_expression,
)


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(-5, -5) == -10
    assert add(2.5, 3.5) == 6.0


def test_subtract():
    assert subtract(10, 5) == 5
    assert subtract(0, 5) == -5
    assert subtract(-5, -5) == 0
    assert subtract(5.5, 2.5) == 3.0


def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
    assert multiply(-4, -5) == 20
    assert multiply(0, 100) == 0
    assert multiply(2.5, 2) == 5.0


def test_divide():
    assert divide(10, 2) == 5.0
    assert divide(-9, 3) == -3.0
    assert divide(5, 2) == 2.5
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


def test_power():
    assert power(2, 3) == 8
    assert power(5, 0) == 1
    assert power(4, 0.5) == 2.0
    assert power(-2, 2) == 4


def test_square_root():
    assert square_root(16) == 4.0
    assert square_root(0) == 0.0
    assert square_root(2.25) == 1.5
    with pytest.raises(ValueError, match="Cannot calculate square root of a negative number"):
        square_root(-4)


def test_modulo():
    assert modulo(10, 3) == 1
    assert modulo(10, 5) == 0
    with pytest.raises(ValueError, match="Cannot perform modulo by zero"):
        modulo(10, 0)


def test_evaluate_expression():
    assert evaluate_expression("10 + 5") == 15.0
    assert evaluate_expression("10 - 2 * 3") == 4.0
    assert evaluate_expression("(10 + 2) * 3") == 36.0
    assert evaluate_expression("-5 + 10") == 5.0
    assert evaluate_expression("2 ** 3") == 8.0
    assert evaluate_expression("10 % 3") == 1.0

    with pytest.raises(ValueError, match="Expression cannot be empty"):
        evaluate_expression("   ")

    with pytest.raises(ValueError, match="Invalid expression syntax"):
        evaluate_expression("10 + ")

    with pytest.raises(ValueError, match="Cannot divide by zero"):
        evaluate_expression("10 / 0")

    with pytest.raises(ValueError, match="Unsupported elements in expression"):
        evaluate_expression("a + b")

    with pytest.raises(ValueError, match="Unsupported elements in expression"):
        evaluate_expression("True + 1")
