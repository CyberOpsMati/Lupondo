import ast
import math
import operator
import sys


def add(a: float, b: float) -> float:
    """Returns the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Returns the difference of a and b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Returns the product of a and b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Returns the quotient of a and b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def power(a: float, b: float) -> float:
    """Returns a raised to the power of b."""
    return a ** b


def square_root(a: float) -> float:
    """Returns the square root of a.

    Raises:
        ValueError: If a is negative.
    """
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number.")
    return math.sqrt(a)


def modulo(a: float, b: float) -> float:
    """Returns the remainder of a divided by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot perform modulo by zero.")
    return a % b


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluate_expression(expression: str) -> float:
    """Safely evaluates an arithmetic expression using AST parsing.

    Args:
        expression: A string containing an arithmetic expression (e.g. "3 + 5 * (2 - 8)").

    Returns:
        The calculated numerical result as a float.

    Raises:
        ValueError: If the expression contains invalid syntax or unsupported elements.
    """
    if not expression or not expression.strip():
        raise ValueError("Expression cannot be empty.")

    try:
        node = ast.parse(expression.strip(), mode='eval').body
    except SyntaxError as e:
        raise ValueError(f"Invalid expression syntax: {e}")

    def _eval_node(node):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
        ):
            return float(node.value)
        elif isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            op_type = type(node.op)
            if op_type in _ALLOWED_OPERATORS:
                if op_type == ast.Div and right == 0:
                    raise ValueError("Cannot divide by zero.")
                if op_type == ast.Mod and right == 0:
                    raise ValueError("Cannot perform modulo by zero.")
                return _ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        elif isinstance(node, ast.UnaryOp):
            operand = _eval_node(node.operand)
            op_type = type(node.op)
            if op_type in _ALLOWED_OPERATORS:
                return _ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        else:
            raise ValueError("Unsupported elements in expression.")

    return _eval_node(node)


def print_menu():
    """Prints the main interactive menu options."""
    print("\n--- Python Calculator ---")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Power (a^b)")
    print("6. Square Root")
    print("7. Modulo")
    print("8. Evaluate Expression")
    print("9. Exit")


def get_float_input(prompt: str) -> float:
    """Helper to prompt user for a float input."""
    while True:
        try:
            val = input(prompt)
            return float(val)
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def cli_main():
    """Runs the interactive CLI loop for the calculator."""
    print("Welcome to the Python Calculator Application!")
    while True:
        print_menu()
        choice = input("Select an option (1-9): ").strip()

        if choice == '9':
            print("Thank you for using Python Calculator. Goodbye!")
            break

        try:
            if choice == '1':
                a = get_float_input("Enter first number: ")
                b = get_float_input("Enter second number: ")
                result = add(a, b)
                print(f"Result: {a} + {b} = {result}")

            elif choice == '2':
                a = get_float_input("Enter first number: ")
                b = get_float_input("Enter second number: ")
                result = subtract(a, b)
                print(f"Result: {a} - {b} = {result}")

            elif choice == '3':
                a = get_float_input("Enter first number: ")
                b = get_float_input("Enter second number: ")
                result = multiply(a, b)
                print(f"Result: {a} * {b} = {result}")

            elif choice == '4':
                a = get_float_input("Enter numerator: ")
                b = get_float_input("Enter denominator: ")
                result = divide(a, b)
                print(f"Result: {a} / {b} = {result}")

            elif choice == '5':
                a = get_float_input("Enter base: ")
                b = get_float_input("Enter exponent: ")
                result = power(a, b)
                print(f"Result: {a} ^ {b} = {result}")

            elif choice == '6':
                a = get_float_input("Enter number: ")
                result = square_root(a)
                print(f"Result: √{a} = {result}")

            elif choice == '7':
                a = get_float_input("Enter number: ")
                b = get_float_input("Enter divisor: ")
                result = modulo(a, b)
                print(f"Result: {a} % {b} = {result}")

            elif choice == '8':
                expr = input("Enter expression (e.g. (10 + 2) * 3): ")
                result = evaluate_expression(expr)
                print(f"Result: {expr} = {result}")

            else:
                print("Invalid choice. Please select a number between 1 and 9.")

        except ValueError as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    cli_main()
