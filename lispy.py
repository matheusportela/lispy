__version__ = '0.0.1'

import re
import readline

def eval(instruction):
    return Lispy().eval(instruction)

class Lispy:
    class LispyError(BaseException): pass

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
            except self.LispyError as e:
                print('ERROR: {}'.format(str(e)))
            except (KeyboardInterrupt, EOFError):
                break
        
        print('\n{}'.format(self.farewell_message))
    
    def _format_output(self, output):
        string = ''
        
        if type(output) == list:
            string += '('
            string += ' '.join([str(self._format_output(o)) if type(o) == list else str(o) for o in output]) 
            string += ')'
        else:
            string = str(output)

        return string


class Lexer:
    class InvalidInputError(Lispy.LispyError): pass

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
    class UnknownSymbolError(Lispy.LispyError): pass

    def __init__(self):
        self.type_parser = {
            'nil': {
                'regex': '^(nil)$',
                'parser': lambda t: None
            },
            'int': {
                'regex': r'^(-?\d+)$',
                'parser': int
            },
            'float': {
                'regex': r'^(-?\d*.\d+)$',
                'parser': float
            },
            'str': {
                'regex': r'^\'(\w+)\'$',
                'parser': str
            },
        }
        self.types = self.type_parser.keys()

    def parse(self, tokens):
        if not tokens:
            return []

        if tokens[0] == 'quote':
            return tokens

        result = [tokens[0]]

        for token in tokens[1:]:
            if type(token) == list:
                result.append(self.parse(token))
            else:
                result.append(self._parse_token(token))

        return result 

    def _parse_token(self, token):
        for type in self.types:
            regex = self.type_parser[type]['regex']
            result = re.match(regex, token)

            if result:
                parser = self.type_parser[type]['parser']
                return parser(result.group(1))

        raise self.UnknownSymbolError('Unknown symbol "{}"'.format(token))
            

class Interpreter:
    class UnknownFunctionError(Lispy.LispyError): pass

    def __init__(self):
        self.functions = {
            'quote': self._quote,
            '+': self._sum,
            'sum': self._sum,
        }
        self.variableS = {}

    def execute(self, instruction):
        if not instruction:
            return None

        function_name = instruction[0]
        args = instruction[1:]

        if function_name != 'quote':
            args = self._evaluate_args(args)

        if function_name in self.functions:
            function = self.functions[function_name]
            return function(*args)

        raise self.UnknownFunctionError('Unknown function "{}"'.format(function_name))
    
    def _evaluate_args(self, args):
        result = []
        
        for arg in args:
            if type(arg) == list:
                arg = self.execute(arg)
        
            result.append(arg)

        return result


    def _quote(self, arg):
        return arg

    def _sum(self, *args):
        return sum(args)


if __name__ == '__main__':
    print('lispy v{}'.format(__version__))
    Lispy().repl()
