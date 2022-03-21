import tkinter as tk

from tokens import *

def pos2d_to_message(pos2d):
    return f" строка {pos2d[0][0]}"


class CustomSyntaxError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SyntaxErrorExpectedVSGot(Exception):
    def __init__(self, expected, got, pos2d=None, before=None, 
        exceptions=None, custom_message=None, after=None,only_custom=False) -> None:
        assert isinstance(expected, (str, list, tuple))
        if isinstance(expected, (list, tuple)):
            expected_str = f"[{' | '.join(expected)}]"
        else:
            expected_str = expected
        if isinstance(exceptions, (list, tuple)):
            exceptions_str = f"[{' | '.join(exceptions)}]"
        else:
            exceptions_str = exceptions
        self.message = "Ошибка:\n\t"
        if custom_message is not None:
            self.message += custom_message + "\n\t"
        if not after in [TYPE_INT, TYPE_ID, TYPE_OPERATOR, TYPE_TERMINAL, T_BOF, T_EOF, T_INT, T_ID]:
            after = f'"{after}"' 
        if not only_custom:
            self.message += f"После {after} не может следовать {got} \n\t(Должно быть {expected_str})"
        if exceptions is not None:
            self.message += f" (кроме {exceptions_str})"
        if got == T_EOF:
            pos2d[0][0] -= 1
        if pos2d is not None:
            self.message += f"\nПоложение: \n\t{pos2d_to_message(pos2d)}"
            
        self.pos2d = pos2d
        super().__init__(self.message)


class SyntaxErrorMaxBracketsDepth(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TokenErrorUnrecognizedToken(Exception):
    def __init__(self, last_token, unrecognized_token, cut=10) -> None:
        self.token = last_token
        pos2d = self.token.pos2d
        pos2d[1] = None
        if pos2d is not None:
            self.message = f"Ошибка: неопознанный токен: {unrecognized_token[:-1]}...'\nПоложение: {pos2d_to_message(pos2d)}"
        else:
            self.message = f"Ошибка: неопознанный токен: {unrecognized_token[:-1]}...'"

        self.pos2d = [pos2d[1], None]
        self.unrecognized_token = unrecognized_token
        super().__init__(self.message)
