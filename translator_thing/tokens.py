#########################################
# Tokens
# Words
T_BEGIN = '"Начало"'
T_END = '"Конец"'
T_ANALYSIS = '"Анализ"'
T_SYNTHESYS = '"Синтез"'
T_ANALYSISEND = '"Конец анализа"'
T_SYNTHESYSEND = '"Конец синтеза"'
T_VARS = '"Переменные"'
T_MARKS = '"Метки"'
T_MARKSEND = '"Конец меток"'
# Values
T_COMPLEX = 'Компл'
T_INT = 'Цел. Знач.'
T_ID = 'Переменная'
# Operators
T_PLUS = '"+"'
T_MINUS ='"-"'
T_MUL = '"*"'
T_DIV = '"/"'
T_COMMA = '","'
T_DOT = '"."'
T_SEMICOLON = '";"'
T_COLON = '":"'
T_LBR = '"("'
T_RBR = '")"'
T_EQ = '"="'
T_SIN = '"sin"'
T_COS = '"cos"'
T_ABS = '"abs"'
T_NBS = '"("'
T_NOT = '"!"'
T_AND = '"&"'
T_OR = '"|"'
# Skip
TS_SPACE = 'Пробел'
TS_NEW_LINE = '"Новая строка"'
TS_TAB = '"Табуляция"'
# Other
T_BOF = 'Начало документа'
T_EOF = 'Конец документа'
#########################################
# Types
TYPE_COMPLEX = 'Компл'
TYPE_INT = 'Цел. Знач.'
TYPE_ID = 'Переменная'
TYPE_OPERATOR = 'Оператор'
TYPE_TERMINAL = 'Терминал'

TYPE_SIN = '"sin"'
TYPE_COS = '"cos"'
TYPE_ABS = '"abs"'
TYPE_PLUS = '+'
TYPE_MINUS ='-'
TYPE_MUL = '*'
TYPE_DIV = '/'
TYPE_DOT = '.'
TYPE_COMMA = ','
TYPE_LBR = '('
TYPE_RBR = ')'
TYPE_EQ = '=:'
TYPE_POW = '^'
TYPE_NOT = '!'
TYPE_AND = '&'
TYPE_OR = '|'
TYPE_SEMICOLON = ';'
TYPE_COLON = ':'

class Pattern(object):
    def __init__(self, re, type, token) -> None:
        super().__init__()
        self.re = re
        self.type = type
        self.token = token

SKIP_PATTERNS = [
    Pattern(R"^\n", "skip", TS_NEW_LINE),
    Pattern(R"^ ", "skip", TS_SPACE),
    Pattern(R"^\t+", "skip", TS_TAB)
]

SKIP_TOKENS = [
    TS_NEW_LINE,
    TS_SPACE,
    TS_TAB
]

# TODO fix errors with marks, variables, integers and real values 
PATTERNS = [
    Pattern(R'^sin', TYPE_SIN, T_SIN),
    Pattern(R'^cos', TYPE_COS, T_COS),
    Pattern(R'^abs', TYPE_ABS, T_ABS),
#########################################
# Other
    # Pattern(R"^\d+:", "mark", T_MARK),
    #Pattern(R'^EXPR', "temp", T_TEMP_EXPR),
#########################################
# Words
    Pattern(R'^Начало', TYPE_TERMINAL, T_BEGIN),
    Pattern(R'^Анализ', TYPE_TERMINAL, T_ANALYSIS),
    Pattern(R'^Синтез', TYPE_TERMINAL, T_SYNTHESYS),
    Pattern(R'^Конец анализа', TYPE_TERMINAL, T_ANALYSISEND),
    Pattern(R'^Конец синтеза', TYPE_TERMINAL, T_SYNTHESYSEND),
    Pattern(R'^Переменные', TYPE_TERMINAL, T_VARS),
    Pattern(R'^Метки', TYPE_TERMINAL, T_MARKS),
    Pattern(R'^Конец меток', TYPE_TERMINAL, T_MARKSEND),
    Pattern(R'^Конец', TYPE_TERMINAL, T_END),
#########################################
# Operands
    Pattern(R'^[0-9]+\.[0-9]+,[0-9]+\.[0-9]+', TYPE_COMPLEX, T_COMPLEX),
    Pattern(R"^[а-яА-Я][а-яА-Я][0-9]+", TYPE_ID, T_ID),
    Pattern(R"^[0-9]+", TYPE_INT, T_INT),
#########################################
# Operators
    # {"re": R"^(\+|\-|\*|\/|\|\||&&|\[|\]|=|,)", "type": TYPE_OPERATOR},
    Pattern(R'^\+', TYPE_PLUS, T_PLUS),
    Pattern(R'^\-', TYPE_MINUS, T_MINUS),
    Pattern(R'^\*', TYPE_MUL, T_MUL),
    Pattern(R'^\/', TYPE_DIV, T_DIV),
    Pattern(R'^\=:', TYPE_EQ, T_EQ),
    Pattern(R'^\,', TYPE_COMMA, T_COMMA),
    Pattern(R'^\.', TYPE_DOT, T_DOT),
    Pattern(R'^\(', TYPE_LBR, T_LBR),
    Pattern(R'^\)', TYPE_RBR, T_RBR),
    Pattern(R'^\:', TYPE_COLON, T_COLON),
    Pattern(R'^\;', TYPE_SEMICOLON, T_SEMICOLON),
    Pattern(R'^\|', TYPE_OR, T_OR),
    Pattern(R'^\&', TYPE_AND, T_AND),
    Pattern(R'^\!', TYPE_NOT, T_NOT),
    
]


class Token(object):
    def __init__(self, type, token, value, pos=None):
        self.type = type
        self.token = token
        self.value = value
        self.pos = pos
        self.pos2d = None
        self.computation_result = None

    def __repr__(self) -> str:
        return str(self.value)

    def compute(self):
        if self.token in (T_INT,):
            return int(str(self.value), base=10)
        elif self.token == T_ID:
            if self.computation_result is not None:
                return self.computation_result
            return None
        else:
            raise Exception(f"compute() не поддерживается для {self.token}")
        
    def update(self, var, val):
        if self.token == T_ID and var.value == self.value:
            self.computation_result = val
