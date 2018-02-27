__version__ = '0.0.1'

import re
import readline

def eval(instruction):
    return Lispy().eval(instruction)

class Lispy:
    class LispyError(BaseException): pass

    def __init__(self):
        # REPL stuff
        self.prompt = '>>> '
        self.welcome_message = ''
        self.farewell_message = 'bye!'

        # Interpreter stuff
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
                self._print(output)
            except (KeyboardInterrupt, EOFError):
                break
            except self.LispyError as e:
                print('ERROR: {}'.format(str(e)))
        
        print('\n{}'.format(self.farewell_message))
    
    def _print(self, output):
        string = ''
        
        if type(output) == list:
            string += '('
            string += ' '.join([str(o) for o in output]) 
            string += ')'
        else:
            string = str(output)

        print(string)


class Lexer:
    class InvalidInputError(Lispy.LispyError): pass

    def tokenize(self, string):
        regex = '^\((.*)\)$'
        result = re.match(regex, string)

        if result:
            token = result.group(1)
            if token:
                return token.split(' ')
            return []
        
        raise self.InvalidInputError('Invalid input "{}"'.format(string))


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

        symbol = tokens[0]
        args = [self._parse_token(token) for token in tokens[1:]]
        return [symbol] + args

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
            'quote': lambda args: args,
            '+': sum,
        }

    def execute(self, instruction):
        if not instruction:
            return None

        function_name = instruction[0]

        if function_name in self.functions:
            function = self.functions[function_name]
            return function(instruction[1:])

        raise self.UnknownFunctionError('Unknown function "{}"'.format(function_name))

if __name__ == '__main__':
    print('lispy v{}'.format(__version__))
    Lispy().repl()
