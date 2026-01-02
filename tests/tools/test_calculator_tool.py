import pytest

from propus.tools import CalculatorTool


@pytest.fixture
def calculator():
    """
    Fixture to initialize the CalculatorTool for each test.
    """
    return CalculatorTool()


# --- BASIC ARITHMETIC ---


def test_basic_arithmetic(calculator):
    """
    Test standard PEMDAS operations and spacing.
    """
    result = calculator.execute("2 + 3 * 4 - (10 / 2)")
    assert result.success is True
    assert result.result["result"] == 9.0


def test_powers_notation(calculator):
    """
    Ensure Python power notation (**) is handled correctly.
    """
    result = calculator.execute("2**3 + 5**2")
    assert result.result["result"] == 33.0


def test_sqrt_and_constants(calculator):
    """
    Test square roots and the constant Pi.
    """
    result = calculator.execute("sqrt(144) + pi")
    # 12 + 3.14159...
    assert pytest.approx(result.result["result"]) == 15.1415926535


# --- STATISTICS & LISTS ---


def test_mean_standard_args(calculator):
    """
    Test mean called with multiple arguments: mean(10, 20, 30).
    """
    result = calculator.execute("mean(10, 20, 30, 40)")
    assert result.result["result"] == 25.0


def test_mean_list_input(calculator):
    """
    Test mean called with a list: mean([10, 20, 30]).
    """
    result = calculator.execute("mean([10, 20, 30, 40])")
    assert result.result["result"] == 25.0


def test_mean_empty_and_single(calculator):
    """
    Test edge cases for statistical functions.
    """
    # Single number
    assert calculator.execute("mean(42)").result["result"] == 42.0
    # Empty call
    assert calculator.execute("mean()").result["result"] == 0.0


# --- NESTING & COMPLEXITY ---


def test_nested_functions(calculator):
    """
    Test combining stats and math functions.
    """
    result = calculator.execute("mean(sqrt(100), sqrt(400))")
    assert result.result["result"] == 15.0


def test_deep_nesting(calculator):
    """
    Test deeply nested operations.
    """
    formula = "sqrt(sqrt(sqrt(65536)))"  # 65536 -> 256 -> 16 -> 4
    result = calculator.execute(formula)
    assert result.result["result"] == 4.0


# --- EDGE CASES & FAILURES ---


def test_large_numbers(calculator):
    """
    Ensure the tool handles large integers via float conversion.
    """
    result = calculator.execute("2**64")
    # 18446744073709551616.0
    assert result.result["result"] == 1.8446744073709552e19 or result.result["result"] == 18446744073709551616.0


def test_unsupported_variables(calculator):
    """
    Verify that variables like 'x' cause a failure.
    """
    # This should raise a NameError because 'x' is not defined in the local_env
    with pytest.raises(Exception):
        calculator.execute("2*x + 5")


def test_precision_decimals(calculator):
    """
    Test small decimal precision.
    """
    result = calculator.execute("1000 * (1.05 ** 2)")
    assert pytest.approx(result.result["result"]) == 1102.5


def test_infinity_is_valid(calculator):
    """
    Infinity should be a successful result returned as a float inf.
    """
    result = calculator.execute("exp(10000)")
    assert result.success is True
    # float(sp.oo.evalf()) becomes float('inf')
    assert result.result["result"] == float("inf")


def test_zoo_is_error(calculator):
    """
    Complex infinity (zoo) should be treated as a failure logic.
    """
    # Based on our simple tool logic, we return success=False for zoo
    result = calculator.execute("1/0")
    assert result.success is False
    assert "error" in result.result
