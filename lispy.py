__version__ = '0.0.1'

import re
import readline


class LispyError(BaseException): pass

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

    def __repr__(self):
        return 'nil'

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
        return self.value[i]

    def __setitem__(self, i, value):
        self._assert_type(value)
        self.value[i] = value

    def __repr__(self):
        return '(' + ' '.join([str(v) for v in self.value]) + ')'

    def _assert_type(self, value):
        if not isinstance(value, Type):
            raise TypeError('Value "{}" is not a valid type'.format(value))

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
                string = input(self.prompt)
                output = self.eval(string)
                print(self._format_output(output))
            except LispyError as e:
                print('ERROR: {}'.format(str(e)))
            except (KeyboardInterrupt, EOFError):
                break

        print('\n{}'.format(self.farewell_message))

    def _format_output(self, output):
        string = ''

        if type(output) == list:
            string += '('
            result = []
            for o in output:
                if type(o) == list:
                    result.append(str(self._format_output(o)))
                elif o == None:
                    result.append('nil')
                else:
                    result.append(str(o))
            string += ' '.join(result)
            string += ')'
        elif output == None:
            string = 'nil'
        else:
            string = str(output)

        return string


class Lexer:
    class InvalidInputError(LispyError): pass

    def tokenize(self, string):
        if not string:
            return []
        elif string[0] == '(':
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
        result = []

        while chars:
            char = chars.pop(0)

            if char in words_delimiters:
                chars.insert(0, char)
                break
            elif char in words_ignores:
                continue
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


class Parser:
    class UnknownSymbolError(LispyError): pass

    def __init__(self):
        self.type_parser = {
            'nil': {
                'regex': '^(nil)$',
                'parser': lambda x: Nil()
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
                'regex': r'^\'(\w+)\'$',
                'parser': lambda x: String(x)
            },
        }
        self.types = self.type_parser.keys()

    def parse(self, tokens):
        if not tokens:
            return []

        result = [Symbol(tokens[0])]

        for token in tokens[1:]:
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
    class UnknownSymbolError(LispyError): pass
    class UnknownFunctionError(LispyError): pass

    def __init__(self):
        self.functions = {
            Symbol('quote'): self._quote,
            Symbol('list'): self._list,
            Symbol('set'): self._set,
            Symbol('get'): self._get,
            Symbol('+'): self._sum,
            Symbol('sum'): self._sum,
        }
        self.variables = {}

    def execute(self, instruction):
        if instruction.__class__ in [Symbol, Integer, Float, String]:
            raise self.UnknownSymbolError('Unknown symbol "{}"'.format(instruction))

        if not instruction:
            return Nil()

        if instruction.__class__ == List:
            function_name = instruction[0]
            args = instruction[1:]

            if function_name != Symbol('quote'):
                args = self._evaluate_args(args)

            if function_name in self.functions:
                function = self.functions[function_name]
                return function(*args)

        raise self.UnknownFunctionError('Unknown function "{}"'.format(function_name))

    def _evaluate_args(self, args):
        result = []

        for arg in args:
            if arg.__class__ in [Symbol, List]:
                arg = self.execute(arg)

            result.append(arg)

        return result

    def _quote(self, arg):
        return arg

    def _list(self, *args):
        return list(args)

    def _set(self, name, value):
        self.variables[name] = value

    def _get(self, name):
        return self.variables[name]

    def _sum(self, *args):
        if all(a.__class__ == Integer for a in args):
            output_class = Integer
        else:
            output_class = Float

        return output_class(sum([a.value for a in args]))


if __name__ == '__main__':
    print('lispy v{}'.format(__version__))
    Lispy().repl()
