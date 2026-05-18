import math
import re


class CalculatorLogic:
    OPERATORS = {"+", "−", "×", "÷", "^"}
    MAX_EXPRESSION_LENGTH = 24

    def __init__(self):
        self.current_expression = "0"
        self.history = []
        self.error_state = False
        self.input_limited = False
        self.max_expression_length = self.MAX_EXPRESSION_LENGTH

    def add_character(self, char):
        if char is None:
            return self.current_expression

        if self.error_state:
            self.clear_all()

        self.input_limited = False
        for raw_ch in str(char):
            ch = self._normalize_char(raw_ch)
            before = self.current_expression
            history_before = len(self.history)
            self._add_single(ch)
            if len(self.current_expression) > self.max_expression_length:
                self.current_expression = before
                while len(self.history) > history_before:
                    self.history.pop()
                self.input_limited = True

        return self.current_expression

    def backspace(self):
        if self.error_state or len(self.current_expression) <= 1:
            self.current_expression = "0"
            self.error_state = False
            return self.current_expression

        self.current_expression = self.current_expression[:-1]
        if not self.current_expression or self.current_expression == "−":
            self.current_expression = "0"
        return self.current_expression

    def evaluate(self):
        raw_expr = self.current_expression
        try:
            expr = self._to_python_expression(raw_expr)
            result = eval(expr, {"__builtins__": {}}, {"math": math})
            final_res = self._format_number(result)

            self.history.append(f"{raw_expr} = {final_res}")
            if len(final_res) > self.max_expression_length:
                self.current_expression = final_res[: self.max_expression_length]
                self.input_limited = True
            else:
                self.current_expression = final_res
            self.error_state = False
            return final_res
        except ZeroDivisionError:
            self.error_state = True
            self.current_expression = "Błąd: Dzielenie przez 0"
            return self.current_expression
        except ValueError:
            self.error_state = True
            self.current_expression = "Błąd: Liczba ujemna"
            return self.current_expression
        except (SyntaxError, TypeError, NameError):
            self.error_state = True
            self.current_expression = "Błąd: Zła składnia"
            return self.current_expression
        except Exception:
            self.error_state = True
            self.current_expression = "Błąd: Zła składnia"
            return self.current_expression

    def clear_all(self):
        self.current_expression = "0"
        self.error_state = False
        self.input_limited = False
        return self.current_expression

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history = []

    def consume_input_limited(self):
        was_limited = self.input_limited
        self.input_limited = False
        return was_limited

    def set_max_expression_length(self, length):
        self.max_expression_length = max(6, int(length))
        if len(self.current_expression) > self.max_expression_length:
            self.current_expression = self.current_expression[: self.max_expression_length]
            self.input_limited = True

    def _normalize_char(self, ch):
        mapping = {"-": "−", "*": "×", "/": "÷"}
        return mapping.get(ch, ch)

    def _add_single(self, ch):
        if ch.isdigit():
            self._add_digit(ch)
            return

        if ch == ".":
            self._add_decimal_point()
            return

        if ch == "√":
            self._sqrt_current_number()
            return

        if ch in self.OPERATORS:
            self._add_operator(ch)

    def _add_digit(self, digit):
        if self.current_expression == "0":
            self.current_expression = digit
            return

        if self.current_expression == "−0":
            self.current_expression = f"−{digit}"
            return

        self.current_expression += digit

    def _add_decimal_point(self):
        _, current_number = self._current_number_info()
        if "." in current_number:
            return

        if self.current_expression == "0":
            self.current_expression = "0."
        elif self.current_expression[-1] in self.OPERATORS:
            self.current_expression += "0."
        else:
            self.current_expression += "."

    def _add_operator(self, operator):
        expr = self.current_expression

        if expr == "0":
            if operator == "−":
                self.current_expression = "−"
            return

        if expr[-1] in self.OPERATORS:
            if operator == "−" and expr[-1] != "−":
                self.current_expression += operator
            else:
                self.current_expression = expr[:-1] + operator
            return

        self.current_expression += operator

    def _sqrt_current_number(self):
        bounds, number_text = self._current_number_info()
        if bounds is None:
            return

        raw_number = number_text
        value = float(number_text.replace("−", "-"))
        if value < 0:
            self.current_expression = "Błąd: Liczba ujemna"
            self.error_state = True
            return

        sqrt_result = self._format_number(math.sqrt(value))
        start, end = bounds
        self.current_expression = f"{self.current_expression[:start]}{sqrt_result}{self.current_expression[end:]}"
        self.history.append(f"√ {raw_number} = {sqrt_result}")

    def _current_number_info(self):
        expr = self.current_expression
        i = len(expr) - 1

        while i >= 0 and (expr[i].isdigit() or expr[i] == "."):
            i -= 1

        start = i + 1
        if start == len(expr):
            return None, ""

        if i >= 0 and expr[i] == "−" and (i == 0 or expr[i - 1] in self.OPERATORS):
            start = i

        return (start, len(expr)), expr[start:]

    def _to_python_expression(self, expression):
        expr = expression.strip()
        if not expr:
            raise SyntaxError

        expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace("−", "-")
        expr = self._convert_roots(expr)
        return expr

    def _convert_roots(self, expression):
        expr = expression
        pattern = re.compile(r"√\s*(-?\d+(?:\.\d+)?)")
        while "√" in expr:
            new_expr, count = pattern.subn(r"math.sqrt(\1)", expr)
            if count == 0:
                raise SyntaxError
            expr = new_expr
        return expr

    def _format_number(self, value):
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return f"{number:.10f}".rstrip("0").rstrip(".")
