__version__ = '0.0.1'

import argparse
import re
import readline


class LispyError(BaseException): pass


class Lispy:
    def __init__(self):
        # REPL attributes
        self.prompt = '>>> '
        self.welcome_message = ''
        self.farewell_message = 'bye!'

        # Interpreter attributes
        self.lexer = Lexer()
        self.parser = Parser()
        self.interpreter = Interpreter()

    def eval(self, string):
        tokens = self.lexer.tokenize(string)
        instruction = self.parser.parse(tokens)
        return self.interpreter.execute(instruction)

    def repl(self):
        readline.parse_and_bind('tab: complete')

        print(self.welcome_message)

        while True:
            try:
                string = self._read_input()
                output = self.eval(string)
                print(self._format_output(output))
            except LispyError as e:
                print('ERROR: {}'.format(str(e)))
            except (KeyboardInterrupt, EOFError):
                break

        print('\n{}'.format(self.farewell_message))

    def _read_input(self):
        buffer = []
        parentheses_difference = 0

        while parentheses_difference > 0 or not buffer:
            indentation = self._calculate_indentation(buffer, parentheses_difference)
            string = input(self.prompt + ' ' * indentation)
            buffer.append(string)
            parentheses_difference += string.count('(') - string.count(')')

        return ' '.join(buffer)

    def _calculate_indentation(self, buffer, parentheses_difference):
        if not buffer:
            return 0

        parenthesis_position = {}

        for string in buffer:
            positions = [i for i, s in enumerate(string) if s == '(']
            for position in positions:
                parenthesis_position[len(parenthesis_position)] = position

        return parenthesis_position[parentheses_difference - 1] + 1  # next space after the parenthesis


    def _format_output(self, output):
        return str(output)

    def execute_script(self, filename):
        with open(filename) as fd:
            string = fd.read().replace('\n', '')

        buffer = []
        open_parentheses = 0

        for c in string:
            if c == '(':
                open_parentheses += 1
            elif c == ')':
                open_parentheses -= 1

            buffer.append(c)

            if open_parentheses == 0:
                self.eval(''.join(buffer))
                buffer = []


class Type:
    def __init__(self, value):
        self._assert_type(value)
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __repr__(self):
        return str(self.value)

    def _assert_type(self, value):
        raise NotImplementedError('Types must implement "_assert_type" method')

class Nil(Type):
    def __init__(self):
        self.value = None

    def __bool__(self):
        return False

    def __repr__(self):
        return 'nil'


class T(Type):
    def __init__(self):
        self.value = True

    def __repr__(self):
        return 't'


class Integer(Type):
    def _assert_type(self, value):
        if type(value) != int:
            raise TypeError('Value "{}" is not an integer'.format(value))

class Float(Type):
    def _assert_type(self, value):
        if type(value) != float:
            raise TypeError('Value "{}" is not a float'.format(value))

class String(Type):
    def _assert_type(self, value):
        if type(value) != str:
            raise TypeError('Value "{}" is not a string'.format(value))

class Symbol(Type):
    def __eq__(self, other):
        return other.__class__ == self.__class__ and self.value == other.value

    def __ne__(self, other):
        return other.__class__ != self.__class__ or self.value != other.value

    def __hash__(self):
        return hash(self.__class__.__name__ + self.value)

    def __repr__(self):
        return ':{}'.format(self.value)

    def _assert_type(self, value):
        if type(value) != str:
            raise TypeError('Value "{}" is not a symbol'.format(value))

class List(Type):
    def __init__(self, *elements):
        [self._assert_type(element) for element in elements]
        self.value = list(elements)

    def __getitem__(self, i):
        if i.__class__ == slice:
            return List(*self.value[i])

        return self.value[i]

    def __setitem__(self, i, value):
        self._assert_type(value)
        self.value[i] = value

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return (v for v in self.value)

    def __repr__(self):
        return '(' + ' '.join([str(v) for v in self.value]) + ')'

    def _assert_type(self, value):
        if not isinstance(value, Type):
            raise TypeError('Value "{}" is not a valid type'.format(value))


class Lexer:
    class InvalidInputError(LispyError): pass

    def tokenize(self, string):
        if not string:
            return []

        string = string.replace('\n', ' ')

        if string[0] == '(':
            return self.tokenize_list(list(string))
        else:
            return self.tokenize_words(list(string))

    def tokenize_list(self, chars):
        result = []
        char = chars.pop(0) # ignore first '('

        while chars:
            char = chars.pop(0)

            if char == ')':
                return result
            elif char == '(':
                chars.insert(0, char)
                result.append(self.tokenize_list(chars))
            else:
                chars.insert(0, char)
                result += self.tokenize_words(chars)

        raise self.InvalidInputError('Invalid input "{}"'.format(''.join(chars)))

    def tokenize_words(self, chars):
        words_delimiters = '()'
        words_ignores = ' '
        literal_delimiters = '"'
        result = []

        while chars:
            char = chars.pop(0)

            if char in words_delimiters:
                chars.insert(0, char)
                break
            elif char in words_ignores:
                continue
            elif char in literal_delimiters:
                chars.insert(0, char)
                result.append(self.tokenize_literal(chars))
            else:
                chars.insert(0, char)
                result.append(self.tokenize_word(chars))

        return result

    def tokenize_word(self, chars):
        word_delimiters = ' ()'
        result = []

        while chars:
            char = chars.pop(0)

            if char in word_delimiters:
                chars.insert(0, char)
                break
            else:
                result.append(char)

        return ''.join(result)

    def tokenize_literal(self, chars):
        literal_delimiters = '"'
        result = []
        char = chars.pop(0) # ignore first '"'
        result.append(char)

        while chars:
            char = chars.pop(0)

            if char in literal_delimiters:
                result.append(char)
                break
            else:
                result.append(char)

        return ''.join(result)


class Parser:
    def __init__(self):
        self.type_parser = {
            'nil': {
                'regex': r'^(nil)$',
                'parser': lambda x: Nil()
            },
            't': {
                'regex': r'^(t)$',
                'parser': lambda x: T()
            },
            'integer': {
                'regex': r'^(-?\d+)$',
                'parser': lambda x: Integer(int(x))
            },
            'float': {
                'regex': r'^(-?\d*.\d+)$',
                'parser': lambda x: Float(float(x))
            },
            'string': {
                'regex': r'^"(.*)"$',
                'parser': lambda x: String(x)
            },
        }
        self.types = self.type_parser.keys()

    def parse(self, tokens):
        if not tokens:
            return Nil()

        result = []

        for token in tokens:
            if type(token) == list:
                result.append(self.parse(token))
            else:
                result.append(self._parse_token(token))

        return List(*result)

    def _parse_token(self, token):
        for type in self.types:
            regex = self.type_parser[type]['regex']
            result = re.match(regex, token)

            if result:
                parser = self.type_parser[type]['parser']
                return parser(result.group(1))

        return Symbol(token)


class Interpreter:
    class UndefinedSymbolError(LispyError): pass
    class UndefinedFunctionError(LispyError): pass
    class UndefinedVariableError(LispyError): pass

    def __init__(self):
        self.global_variable_context = {}
        self.local_variable_contexts = []

        self.special_functions = {
            Symbol('quote'): self._quote,
            Symbol('defun'): self._defun,
            Symbol('if'): self._if,
            Symbol('let'): self._let,
            Symbol('progn'): self._progn,
            Symbol('set'): self._set,
            Symbol('get'): self._get,
        }
        self.regular_functions = {
            Symbol('list'): self._list,
            Symbol('car'): self._car,
            Symbol('cdr'): self._cdr,
            Symbol('cons'): self._cons,
            Symbol('eq'): self._equal,
            Symbol('='): self._equal,
            Symbol('+'): self._sum,
            Symbol('sum'): self._sum,
            Symbol('-'): self._sub,
            Symbol('sub'): self._sub,
            Symbol('*'): self._mul,
            Symbol('mul'): self._mul,
            Symbol('/'): self._div,
            Symbol('div'): self._div,
            Symbol('pow'): self._pow,
            Symbol('write'): self._write,
            Symbol('read'): self._read,
            Symbol('concat'): self._concat,
            Symbol('float'): self._float,
            Symbol('int'): self._int,
            Symbol('str'): self._str,
        }
        self.functions = {**self.special_functions, **self.regular_functions}

    def execute(self, instruction):
        if instruction.__class__ in [Symbol, Integer, Float, String]:
            raise self.UndefinedSymbolError('Undefined symbol "{}"'.format(instruction))

        if instruction == Nil():
            return Nil()

        if instruction.__class__ == List:
            function_name = instruction[0]
            args = instruction[1:]

            if function_name == Nil():
                return Nil()

            if function_name == T():
                return T()

            if function_name in self.regular_functions:
                args = self._evaluate_args(args)

            if function_name in self.functions:
                function = self.functions[function_name]
                result = function(*args)
                return result if result != None else Nil()

        raise self.UndefinedFunctionError('Undefined function "{}"'.format(function_name))

    def _evaluate_args(self, args):
        result = []

        for arg in args:
            if arg.__class__ == List:
                arg = self.execute(arg)
            elif arg.__class__ == Symbol:
                arg = self._get_variable(arg) if self._is_variable(arg) else self.execute(arg)

            result.append(arg)

        return result

    def _get_variable(self, name):
        local_variable_context = self._find_local_variable_context(name)
        if local_variable_context is not None:
            return local_variable_context[name]
        elif self._is_global_variable(name):
            return self._get_global_variable(name)
        raise self.UndefinedVariableError('Undefined variable "{}"'.format(name))

    def _is_variable(self, name):
        return self._is_global_variable(name) or self._is_local_variable(name)

    def _get_global_variable(self, name):
        return self.global_variable_context[name]

    def _set_global_variable(self, name, value):
        self.global_variable_context[name] = value

    def _is_global_variable(self, name):
        return name in self.global_variable_context

    def _get_local_variable(self, name):
        local_variable_context = self._find_local_variable_context(name)
        if local_variable_context is not None:
            return local_variable_context[name]
        raise self.UndefinedVariableError('Undefined local variable "{}"'.format(name))

    def _set_local_variable(self, name, value):
        self.local_variable_contexts[0][name] = value

    def _is_local_variable(self, name):
        return self._find_local_variable_context(name) is not None

    def _find_local_variable_context(self, name):
        for local_variable_context in self.local_variable_contexts:
            if name in local_variable_context:
                return local_variable_context
        return None

    def _create_local_variable_context(self):
        self.local_variable_contexts.insert(0, {})

    def _delete_local_variable_context(self):
        self.local_variable_contexts.pop(0)

    def _evaluate_if_list(self, param):
        return self.execute(param) if param.__class__ == List else param

    # Functions
    def _quote(self, arg):
        return arg

    def _list(self, *args):
        if not len(args):
            return Nil()
        return List(*args)

    def _car(self, l):
        if l.__class__ == Nil or len(l) < 1:
            return Nil()
        return l[0]

    def _cdr(self, l):
        if l.__class__ == Nil:
            return Nil()

        result = l[1:]

        if not len(result):
            return Nil()

        return result

    def _cons(self, value, list):
        if not list:
            return List(value)
        return List(value, *list)

    def _set(self, name, value):
        self._set_global_variable(name, self._evaluate_if_list(value))

    def _get(self, name):
        return self._get_global_variable(name)

    def _equal(self, x, y):
        return T() if x == y else Nil()

    def _sum(self, *args):
        output_class = self._cast_arithmetic_values(args)
        return output_class(sum([a.value for a in args]))

    def _sub(self, x, y=None):
        if y:
            output_class = self._cast_arithmetic_values([x, y])
            result = output_class(x.value - y.value)
        else:
            x.value *= -1
            result = x

        return result

    def _mul(self, *args):
        output_class = self._cast_arithmetic_values(args)
        result = 1
        for arg in args:
            result *= arg.value
        return output_class(result)

    def _cast_arithmetic_values(self, args):
        if all(a.__class__ == Integer for a in args):
            output_class = Integer
        else:
            output_class = Float

        return output_class

    def _div(self, x, y):
        return Float(x.value / y.value)

    def _pow(self, x, y):
        output_class = self._cast_arithmetic_values([x, y])
        return output_class(x.value**y.value)

    def _let(self, var_defs, *instructions):
        self._create_local_variable_context()

        for name, value in var_defs:
            self._set_local_variable(name, value)

        result = Nil()
        for instruction in instructions:
            result = self.execute(instruction)

        self._delete_local_variable_context()

        return result

    def _defun(self, function_name, arg_names, instructions):
        def function(*arg_values):
            values = [self._evaluate_if_list(a) for a in arg_values]
            var_defs = zip(arg_names, values)
            return self._let(var_defs, instructions)
        self.functions[function_name] = function
        return function_name

    def _if(self, condition, true_expr, false_expr=Nil()):
        condition_result = self._evaluate_if_list(condition)

        if condition_result != Nil():
            result = self._evaluate_if_list(true_expr)
        else:
            result = self._evaluate_if_list(false_expr)

        return result

    def _write(self, arg, end='\n'):
        if end == Nil():
            end = ''
        print(arg, end=end)
        return Nil()

    def _read(self):
        return String(input())

    def _progn(self, *instructions):
        result = Nil()
        for instruction in instructions:
            result = self.execute(instruction)

        return result

    def _concat(self, *args):
        strings = [arg.value for arg in args]
        return String(''.join(strings))

    def _float(self, arg):
        return Float(float(arg.value))

    def _int(self, arg):
        return Integer(int(float(arg.value)))

    def _str(self, arg):
        return String(str(arg.value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='lispy v{}'.format(__version__))
    parser.add_argument('filename', nargs='?', help='program read from script file')
    args = parser.parse_args()

    if args.filename:
        Lispy().execute_script(args.filename)
    else:
        print('lispy v{}'.format(__version__))
        Lispy().repl()
