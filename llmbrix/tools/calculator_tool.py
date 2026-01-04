import sympy as sp

from llmbrix.tool_calling.base_tool import BaseTool
from llmbrix.tool_calling.tool_output import ToolOutput
from llmbrix.tool_calling.tool_param import ToolParam
from llmbrix.tool_calling.tool_param_types import ToolParamTypes

TOOL_NAME = "calculator"
TOOL_DESC = "Computes numerical results for math formulas and averages."
PARAM_DESC = (
    "The mathematical formula to calculate. Supports arithmetic, powers (**), "
    "and functions like sqrt(), mean(), and median(). "
    "Examples: 'mean(10, 20, 30)', 'sqrt(144) * 2', '(5 + 5) ** 2'."
)


class CalculatorTool(BaseTool):
    """
    A calculator tool that evaluates numerical formulas and statistical expressions.
    Does not support variables, only direct math operations.
    """

    def __init__(self, name=TOOL_NAME, desc=TOOL_DESC, param_desc=PARAM_DESC):
        params = [ToolParam(name="formula", description=param_desc, type=ToolParamTypes.STRING, required=True)]

        super().__init__(
            name=name,
            description=desc,
            params=params,
        )

    def execute(self, formula: str, **kwargs) -> ToolOutput:
        local_env = {
            "mean": lambda *args: (
                sum(args[0]) / len(args[0]) if args and isinstance(args[0], (list, tuple)) else sum(args) / len(args)
            )
            if args
            else 0,
            "sqrt": sp.sqrt,
            "pi": sp.pi,
            "exp": sp.exp,
        }
        result_obj = sp.sympify(formula, locals=local_env)

        if not hasattr(result_obj, "evalf"):
            result_obj = sp.sympify(result_obj)

        if result_obj == sp.zoo:
            return ToolOutput(success=False, result={"error": "Division by zero."})

        res = float(result_obj.evalf())

        return ToolOutput(success=True, result={"formula": formula, "result": res})
