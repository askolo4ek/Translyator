from tkinter import Variable
from tokens import *
from utils import convert2serialize
import json
import math

class Node(object):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return super().__repr__()

    def to_json(self) -> str:
        return json.dumps(convert2serialize(self))


class NodeSpaceSeparatedValues(Node):
    def __init__(self, element, next_element) -> None:
        super().__init__()
        self.element = element
        self.next_element = next_element
    
    def __repr__(self) -> str:
        if self.next_element is not None:
            return f"{self.element} {self.next_element}"
        else:
            return str(self.element)


class NodeFloatValues(Node):
    def __init__(self, element, next_element) -> None:
        super().__init__()
        self.element = element
        self.next_element = next_element

    def __repr__(self) -> str:
        if self.next_element is not None:
            return f"{self.element}.{self.next_element}"
        else:
            return str(self.element)




class NodeBinaryOperator(Node):
    def __init__(self, left, operator, right, precedence_priority=-1) -> None:
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
        self.precedence_priority = precedence_priority

    def __repr__(self) -> str:
        return f"{self.left} {self.operator} {self.right}"

    def compute(self):
        flag = True
        while flag:
            if isinstance(self.right, NodeBinaryOperator):
                if self.precedence_priority == self.right.precedence_priority:
                    flag = True
                    new_left = NodeBinaryOperator(self.left, self.operator, self.right.left, self.precedence_priority)
                    new_operator = self.right.operator
                    new_right = self.right.right
                    self.left, self.right, self.operator = new_left, new_right, new_operator
                else:
                    flag = False
            else:
                flag = False

        left = self.left.compute()
        right = self.right.compute()
        
        return(self.compute_binary_operation(self.operator, left, right))   
        

    def update(self, variable, computation_result):
        self.left.update(variable, computation_result)
        self.right.update(variable, computation_result)


    @staticmethod
    def compute_binary_operation(operator, left, right):
        if left is not None and right is not None:
            if operator.token == T_MUL:
                result = left * right
            elif operator.token == T_DIV:
                result = left / right
            if operator.token == T_PLUS:
                result = left + right
            elif operator.token == T_MINUS:
                result = left - right
            elif operator.token == T_AND:
                result = left and right
            elif operator.token == T_OR:
                result = left or right
            return result
        else:
            return None
        
class NodeUnaryOperator(Node):
    def __init__(self, operator, term) -> None:
        super().__init__()
        self.operator = operator
        self.term = term

    def __repr__(self) -> str:
        return f"{self.operator}({self.term})"

    def compute(self):
        term = self.term.compute()

        if term is not None:
            if self.operator.token == T_NOT:
                result = not bool(term)
            elif self.operator.token == T_MINUS:
                result = - term
            elif self.operator.token == T_SIN:
                return math.sin(term)
            elif self.operator.token == T_COS:
                return math.cos(term)
            elif self.operator.token == T_ABS:
                return abs(term)
            return result
        else:
            return None
    
    def update(self, variable, computation_result):
        self.term.update(variable, computation_result)

class NodeFunction(Node):
    def __init__(self, expression, t_func) -> None:
        super().__init__()
        self.param = expression
        self.t_func = t_func

    def __repr__(self) -> str:
        return f"{self.t_func}{self.param})"

    def compute(self):
        computation_res = self.param.compute()
        if computation_res == None:
            return None
        if self.t_func.token == T_SIN:
            return math.sin(computation_res)
        elif self.t_func.token == T_COS:
            return math.cos(computation_res)
        elif self.t_func.token == T_ABS:
            return abs(computation_res)
        elif self.t_func.token == T_NBS:
            return computation_res


    def update(self, variable, computation_result):
        self.param.update(variable, computation_result)

class NodeExpression(Node):
    def __init__(self, expression) -> None:
        super().__init__()
        self.expression = expression

    def __repr__(self) -> str:
        return f"({self.expression})"

    def compute(self):
        return self.expression.compute()
            
    def update(self, variable, computation_result):
        self.expression.update(variable, computation_result)

class NodeMark(NodeSpaceSeparatedValues):
    def __init__(self, element, next_element) -> None:
        super().__init__(element, next_element)

class NodeVar(NodeSpaceSeparatedValues):
    def __init__(self, element, next_element) -> None:
        super().__init__(element, next_element)


class NodeOperation(Node):
    def __init__(self, variable, expression=None, next_operation=None, root_operation=None) -> None:
        super().__init__()
        self.variable = variable
        #self.marks = marks
        self.expression = expression
        self.next_operation = next_operation
    
    def __repr__(self) -> str:
        #s = f"{self.marks} : {self.variable} = {self.expression} "
        s = f"{self.variable} = {self.expression} "
        if self.next_operation is not None:
            s += str(self.next_operation)
        return s

    def compute(self):
        result = self.expression.compute()
        if result is not None:
            message = f"Переменная {self.variable} = {result}\n"
            self.variable.update(self.variable, result)
            if self.next_operation is not None:
                self.next_operation.update(self.variable, result)
                message += self.next_operation.compute()[1]
        else:
            message = f"Переменная {self.variable} - Ошибка, в связанных вычислениях используется неопределённая переменная"
        return result, message
        
    def update(self, variable, computation_result):
        self.expression.update(variable, computation_result)
        if self.next_operation is not None:
            self.next_operation.update(variable, computation_result)
    

class NodeNamedSet(Node):
    def __init__(self, element, next_named_set) -> None:
        super().__init__()
        assert isinstance(
            element, 
            (
                NodeMark, 
                NodeVar
            )
        ), f"Unsupported element type {type(element)} for NamedSet"
        self.element = element
        self.next_named_set = next_named_set
    
    def __repr__(self) -> str:
        if isinstance(self.element, NodeMark):
            return f'"Метки" {self.element} {self.next_named_set} "Конец меток"'
        elif isinstance(self.element, NodeVar):
            return f'"Переменные" {self.element} {self.next_named_set}'


class NodeProgram(Node):
    def __init__(
        self, 
        named_set: NodeNamedSet, 
        operations: NodeOperation
    ) -> None:
        super().__init__()
        self.named_set = named_set
        self.operations = operations
    
    def __repr__(self) -> str:
        return f'"Начало" {self.named_set} {self.operations} "Конец"'