from re import A
from typing import Iterable, List
from tokenizer import *
from nodes import *
from errors import CustomSyntaxError, SyntaxErrorExpectedVSGot, SyntaxErrorMaxBracketsDepth


class Parser():
    def __init__(self, tokens: List, max_brackets_depth=50) -> None:
        assert max_brackets_depth >= -1
        self.tokens = tokens
        self.max_brackets_depth = max_brackets_depth
        self.reset()

    def reset(self):
        self._pos = 0
        self._current = self.tokens[self._pos]

    def next(self, n=1):
        assert n >= 1, f"{n} < 1"
        self._pos += n
        if self._pos < len(self.tokens):
            self._current = self.tokens[self._pos]
            if self._current.type == "skip":
                return self.next()
        else:
            self._current = None
        return self._current

    def prev(self, n=1):
        assert n >= 1, f"{n} < 1"
        self._pos -= n
        if self._pos >= 0:
            self._current = self.tokens[self._pos]
            if self._current.type == "skip" and not self._current.token == T_BOF:
                return self.prev()
        else:
            self._current = None
        return self._current
    
    def ast(self):
        self.reset()
        try:
            tree = self.program()
        except (SyntaxErrorExpectedVSGot, SyntaxErrorMaxBracketsDepth) as e:
            return None, e
        else:
            return tree, None
    
    def named_set(self, al_one=False) -> NodeNamedSet:
        expected = (T_ANALYSIS, T_SYNTHESYS,)

        if self._current.token in expected:  #Переменные
            self.next()
            #set_element = self.var_declaration()
            set_element = self.mark_declaration()
            if self._current.token == T_SEMICOLON:
                self.next()
            #set_element = self.complex_declaration()
                if self._current.token in expected:
                    next_named_set = self.named_set(True)
                elif self._current.token == T_ID:
                    raise SyntaxErrorExpectedVSGot([T_ANALYSIS, T_SYNTHESYS], self._current.token,
                                                   pos2d=self._current.pos2d, after=self.prev().value)
            elif not self._current.token == T_ID:
                raise SyntaxErrorExpectedVSGot([T_ANALYSIS, T_SYNTHESYS], self._current.token,
                                               pos2d=self._current.pos2d, after=self.prev().value)
            else:
                next_named_set = None

            return NodeNamedSet(set_element, next_named_set)

        # elif self._current.token == T_SYNTHESYS:    #Метки
        #     self.next()
        #     set_element = self.mark_declaration()
        #     next_named_set = self.named_set(True)
        #     return NodeNamedSet(set_element, next_named_set)
        elif al_one:
            return None
        raise SyntaxErrorExpectedVSGot([T_MARKS, T_VARS], self._current.token, pos2d=self._current.pos2d, after=self.prev().value)
    
    def term(self):
        expected_values = (T_INT, T_ID)
        expected_unary_operators = (T_NOT, T_SIN, T_COS, T_ABS)
        #expected_functions = (T_SIN, T_COS, T_ABS, T_NBS)

        if self._current.token in expected_values:
            term = self._current
            self.next()
            return term
        elif self._current.token in expected_unary_operators:
            operator = self._current
            self.next()
            term = self.term()
            return NodeUnaryOperator(operator, term)
        # elif self._current.token in expected_functions:
        #     func = self._current
        #     self.next()
        #     term = self.expression(exit=(T_RBR, T_END, T_SEMICOLON))
        #     # if self._current.token == T_RBR:
        #     #     self.next()
        #     return NodeFunction(term, func)
            #raise SyntaxErrorExpectedVSGot(T_RBR, self._current.token, pos2d=self._current.pos2d, after=self.prev().type)
        elif self._current.type == TYPE_OPERATOR:
            raise SyntaxErrorExpectedVSGot(
                (TYPE_INT, TYPE_ID, T_LBR, T_NOT,), self._current.token, pos2d=self._current.pos2d, after=self.prev().type   
            )
        
        raise SyntaxErrorExpectedVSGot((TYPE_INT, TYPE_ID, T_LBR, T_NOT,), self._current.token, pos2d=self._current.pos2d, after=self.prev().type)
       
    def binary_expressions(self, expected: tuple, term_function, exit_token: tuple, term_function_kwargs={}, minus=False, precedence_priority=-1):
        first_minus_operator = None
        if minus and self._current.token == T_MINUS:
            first_minus_operator = self._current
            self.next()
        left = term_function(**term_function_kwargs)
        if first_minus_operator is not None:
            left = NodeUnaryOperator(first_minus_operator, left)
        if self._current.token in expected:
            operator = self._current
            self.next()
            right = self.binary_expressions(expected, term_function, exit_token, term_function_kwargs, precedence_priority = precedence_priority)
            return NodeBinaryOperator(left, operator, right, precedence_priority)
        elif self._current.token in exit_token:
            return left
        elif self._current.type in (TYPE_INT, TYPE_ID,):
            raise SyntaxErrorExpectedVSGot([TYPE_OPERATOR + " (кроме отрицания)"], self._current.token, pos2d=self._current.pos2d, after=self.prev().type)
        # elif self._current.token == T_RBR:
        #     raise SyntaxErrorExpectedVSGot([TYPE_OPERATOR + " (кроме отрицания)"], self._current.token, pos2d=self._current.pos2d, after=self.prev().type,
        #     custom_message="\")\" ничего не закрывает")
        raise SyntaxErrorExpectedVSGot([TYPE_OPERATOR + " (кроме отрицания)"], self._current.token, pos2d=self._current.pos2d, after=self.prev().type)

    def expression(self, exit=(T_END, T_SEMICOLON,)):  
        expression = self.binary_expressions(
            expected=(T_PLUS, T_MINUS), 
            term_function=self.binary_expressions,
            exit_token=exit,
            minus=True,
            precedence_priority = 0,
            term_function_kwargs={
                "expected": (T_MUL, T_DIV),
                "term_function": self.binary_expressions,
                "exit_token": (T_PLUS, T_MINUS) + exit,
                "precedence_priority": 1,
                "term_function_kwargs": {
                    "expected": (T_AND, T_OR, T_NOT),
                    "term_function": self.term,
                    "exit_token": (T_PLUS, T_MINUS, T_MUL, T_DIV) + exit,
                    "precedence_priority": 2
                }
            }
        )
        return NodeExpression(expression)


    def var_declaration(self, one_exists=False):
        if self._current.token == T_ID:
            element = self._current
            self.next()
            next_element = self.var_declaration(one_exists=True)
            return NodeVar(element, next_element)
        elif one_exists:
            return None
        
        raise SyntaxErrorExpectedVSGot(T_ID, self._current.token, pos2d=self._current.pos2d, after=self.prev().value)

    def complex_declaration(self, one_exists=False):
        expected = (T_SYNTHESYSEND, T_ANALYSISEND)
        self.float_value()
        if self._current.token in expected:
            self.next()
            return None


    def mark_declaration(self, one_exists=False):
        expected = (T_SYNTHESYSEND, T_ANALYSISEND)
        if self._current.token == T_COMPLEX:
            element = self._current
            self.next()
            next_element = self.mark_declaration(one_exists=True)
            return NodeMark(element, next_element)
        elif one_exists and self._current.token in expected:
            self.next()  #
            # if self._current.token == T_SEMICOLON:
            #     self.next()
            #     return None
            return None
        if one_exists:
            expected = (T_COMPLEX,) + expected
        else:
            expected = (T_COMPLEX,)
        raise SyntaxErrorExpectedVSGot(expected , self._current.token, pos2d=self._current.pos2d, after=self.prev().value)


    def float_value(self, one_exists = False):
        expected = (T_DOT,)
        if self._current.token == T_INT:
            element = self._current
            self.next()
            next_element = self.float_value(one_exists=True)
            return NodeFloatValues(element, next_element)
        elif one_exists and self._current.token in expected:
            self.next()
            if self._current.token == T_INT:
                return None
        if one_exists:
            expected = (T_INT,) + expected
        else:
            expected = (T_INT,)
        raise SyntaxErrorExpectedVSGot(expected, self._current.token, pos2d=self._current.pos2d,
                                       after=self.prev().value)



    def mark(self, one_exists = False):
        expected = (T_COLON,)
        if self._current.token == T_INT:
            element = self._current
            self.next()
            next_element = self.mark(one_exists = True)
            return NodeMark(element, next_element)
        elif one_exists and self._current.token in expected:
            return None
        if one_exists:
            expected = (T_INT,) + expected
        else:
            expected = (T_INT,)
        raise SyntaxErrorExpectedVSGot(expected , self._current.token, pos2d=self._current.pos2d, after=self.prev().value)


    def operation(self,number_of_operations=0) -> NodeOperation:
        #marks = self.mark()
        # if self._current.token == T_COLON:
        #     self.next()
        if self._current.token == T_ID:
            variable = self._current
            self.next()
            if self._current.token == T_EQ:
                self.next()
                expression = self.expression()
                next_expression = None
                    # if self._current.token == T_SEMICOLON:
                    #     self.next()
                    #     next_expression = self.operation(number_of_operations + 1)
                    # else:
                    #     next_expression = None
                return NodeOperation(variable, expression, next_expression)
            else:
                raise SyntaxErrorExpectedVSGot(T_EQ, self._current.token, pos2d=self._current.pos2d, after=self.prev().value)
        elif number_of_operations >= 1:
            return None
        raise SyntaxErrorExpectedVSGot(T_ID, self._current.token, pos2d=self._current.pos2d, after=self.prev().value)
        # elif self._current.token == T_END and number_of_operations >= 1:
        #     return None
        #raise SyntaxErrorExpectedVSGot(T_COLON, self._current.token, pos2d=self._current.pos2d, after=self.prev().value)




    def program(self) -> NodeProgram:
        self.next()
        if self._current.token == T_BEGIN:
            self.next()
            named_set = self.named_set()
            operation = self.operation()
            if self._current.token == T_END:
                self.next()
                while self._current.token in SKIP_TOKENS:
                    self.next()
                if self._current.token == T_EOF:
                    return NodeProgram(named_set, operation)
                else:
                    raise SyntaxErrorExpectedVSGot(T_EOF, self._current.token, pos2d=self._current.pos2d, after=self.prev().value,
                    custom_message="После \"Конец\" ничего не ожидалось", only_custom=True)
            else:
                raise SyntaxErrorExpectedVSGot(T_END, self._current.token, pos2d=self._current.pos2d, after=self.prev().value)
        print(self._current)
        raise SyntaxErrorExpectedVSGot(T_BEGIN, self._current.token, pos2d=self._current.pos2d, after=self.prev().token)