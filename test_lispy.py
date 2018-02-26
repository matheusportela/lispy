import unittest

import lispy


class TestLispy(unittest.TestCase):
    def test_empty_list_returns_none(self):
        self.assertEqual(lispy.eval('()'), None) 

    def test_function_execution(self):
        self.assertEqual(lispy.eval('(+ 1 2 3)'), 6)

    #def test_list_with_nil(self):
    #    self.assertEqual(lispy.eval('(nil)'), [None])

    #def test_list_with_int(self):
    #    self.assertEqual(lispy.eval('(1)'), [1])

    #def test_list_with_float(self):
    #    self.assertEqual(lispy.eval('(1.0)'), [1.0])
    
    #def test_list_with_str(self):
    #    self.assertEqual(lispy.eval("('abc')"), ['abc'])
    
    #def test_list_with_multiple_types(self):
    #    self.assertEqual(lispy.eval("(1 2.0 'abc' nil)"), [1, 2.0, 'abc', None])


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = lispy.Lexer()

    def test_empty_list(self):
        self.assertEqual(self.lexer.tokenize('()'), [])

    def test_list_with_one_element(self):
        self.assertEqual(self.lexer.tokenize('(nil)'), ['nil'])

    def test_list_with_two_elements(self):
        self.assertEqual(self.lexer.tokenize('(1 2)'), ['1', '2'])

    def test_raises_error_on_unbalanced_parentheses(self):
        with self.assertRaises(lispy.Lexer.InvalidInputError):
            self.lexer.tokenize('( 1')


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = lispy.Parser()

    def test_empty_list(self):
        self.assertEqual(self.parser.parse([]), [])

    def test_first_element_is_not_parsed(self):
        self.assertEqual(self.parser.parse(['nil']), ['nil'])

    def test_nil_as_none(self):
        self.assertEqual(self.parser.parse(['quote', 'nil']), ['quote', None])

    def test_1_as_int(self):
        self.assertEqual(self.parser.parse(['quote', '1']), ['quote', 1])

    def test_1_1_as_float(self):
        self.assertEqual(self.parser.parse(['quote', '1.1']), ['quote', 1.1])

    def test_0_1_as_float(self):
        self.assertEqual(self.parser.parse(['quote', '.1']), ['quote', 0.1])

    def test_a_as_str(self):
        self.assertEqual(self.parser.parse(['quote', "'a'"]), ['quote', 'a'])

    def test_abc_as_str(self):
        self.assertEqual(self.parser.parse(['quote', "'abc'"]), ['quote', 'abc'])


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = lispy.Interpreter()

    def test_raises_error_on_unknown_function(self):
        with self.assertRaises(lispy.Interpreter.UnknownFunctionError):
            self.interpreter.execute(['abc', 1, 2])

    def test_sum_two_ints(self):
        self.assertEqual(self.interpreter.execute(['+', 1, 2]), 3)

    def test_sum_two_floats(self):
        self.assertEqual(self.interpreter.execute(['+', 1.0, 1.5]), 2.5)

    def test_sum_multiple_ints_and_floats(self):
        self.assertEqual(self.interpreter.execute(['+', 1, 2.5, -3, -1.25]), -0.75)

    def test_quote_return_same_list(self):
        self.assertEqual(self.interpreter.execute(['quote', 1, 2, 3]), [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
