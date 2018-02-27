import unittest

import lispy


class TestLispy(unittest.TestCase):
    def setUp(self):
        self.lispy = lispy.Lispy()

    def test_empty_list_returns_none(self):
        self.assertEqual(self.lispy.eval('()'), None)

    def test_list_function_without_args(self):
        self.assertEqual(self.lispy.eval('(list)'), [])

    def test_list_function_with_one_arg(self):
        self.assertEqual(self.lispy.eval('(list 1)'), [1])

    def test_list_function_with_multiple_args(self):
        self.assertEqual(self.lispy.eval('(list 1 2 3)'), [1, 2, 3])

    def test_list_evaluate_args(self):
        with self.assertRaises(lispy.Parser.UnknownSymbolError):
            self.lispy.eval('(list 1 2 foo)')

    def test_sum_with_multiple_numbers(self):
        self.assertEqual(self.lispy.eval('(+ 1 2 3)'), 6)

    def test_sum_with_nested_lists(self):
        self.assertEqual(self.lispy.eval('(+ 1 2 (+ 3 4 5) (+ 6 7 8))'), 36)

    def test_quote_does_not_evaluate_symbols(self):
        self.assertEqual(self.lispy.eval('(quote foo)'), 'foo')

    def test_quote_does_not_evaluate_lists(self):
        self.assertEqual(self.lispy.eval('(quote (foo bar))'), ['foo', 'bar'])

    def test_set_and_get_variable_values(self):
        self.lispy.eval('(set (quote *foo*) 42)')
        self.assertEqual(self.lispy.eval('(get (quote *foo*))'), 42)


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = lispy.Lexer()

    def test_tokenize_with_empty_string(self):
        self.assertEqual(self.lexer.tokenize(''), [])

    def test_tokenize_with_single_word(self):
        self.assertEqual(self.lexer.tokenize('abc'), ['abc'])

    def test_tokenize_returns_all_words(self):
        self.assertEqual(self.lexer.tokenize('abc def'), ['abc', 'def'])

    def test_tokenize_with_opening_parenthesis(self):
        self.assertEqual(self.lexer.tokenize('abc)def'), ['abc'])

    def test_tokenize_with_closing_parenthesis(self):
        self.assertEqual(self.lexer.tokenize('abc(def'), ['abc'])

    def test_tokenize_with_empty_list(self):
        self.assertEqual(self.lexer.tokenize('()'), [])

    def test_tokenize_list_with_one_element(self):
        self.assertEqual(self.lexer.tokenize('(nil)'), ['nil'])

    def test_tokenize_list_with_two_elements(self):
        self.assertEqual(self.lexer.tokenize('(1 2)'), ['1', '2'])

    def test_nested_lists(self):
        self.assertEqual(self.lexer.tokenize('((1 2) ((3 4) 5 6))'), [['1', '2'], [['3', '4'], '5', '6']])

    def test_raises_error_on_unbalanced_parentheses(self):
        with self.assertRaises(lispy.Lexer.InvalidInputError):
            self.lexer.tokenize('(1')


class TestParser(unittest.TestCase):
    def setUp(self):
     self.parser = lispy.Parser()

    def assert_none(self, value):
        self.assertEqual(value.__class__.__name__, 'NoneType')

    def assert_int(self, value):
        self.assertEqual(type(value), int)

    def assert_float(self, value):
        self.assertEqual(type(value), float)

    def assert_str(self, value):
        self.assertEqual(type(value), str)

    def test_empty_list(self):
        self.assertEqual(self.parser.parse([]), [])

    def test_first_element_is_not_parsed(self):
        self.assertEqual(self.parser.parse(['nil']), ['nil'])

    def test_nil_as_none(self):
        result = self.parser.parse(['sum', 'nil'])[1]
        self.assertEqual(result, None)
        self.assert_none(result)

    def test_1_as_int(self):
        result = self.parser.parse(['sum', '1'])[1]
        self.assertEqual(result, 1)
        self.assert_int(result)

    def test_negative_1_as_int(self):
        result = self.parser.parse(['sum', '-1'])[1]
        self.assertEqual(result, -1)
        self.assert_int(result)

    def test_1_1_as_float(self):
        result = self.parser.parse(['sum', '1.1'])[1]
        self.assertEqual(result, 1.1)
        self.assert_float(result)

    def test_0_1_as_float(self):
        result = self.parser.parse(['sum', '.1'])[1]
        self.assertEqual(result, 0.1)
        self.assert_float(result)

    def test_negative_1_1_as_float(self):
        result = self.parser.parse(['sum', '-1.1'])[1]
        self.assertEqual(result, -1.1)
        self.assert_float(result)

    def test_a_as_str(self):
        result = self.parser.parse(['sum', "'a'"])[1]
        self.assertEqual(result, 'a')
        self.assert_str(result)

    def test_abc_as_str(self):
        result = self.parser.parse(['sum', "'abc'"])[1]
        self.assertEqual(result, 'abc')
        self.assert_str(result)

    def test_nested_lists(self):
        result = self.parser.parse(['sum', 'nil', ['sum', ['sum', '2', '3.0'], "'abc'"]])

        self.assertEqual(result[1], None)
        self.assertEqual(result[2][1][1], 2)
        self.assertEqual(result[2][1][2], 3.0)
        self.assertEqual(result[2][2], 'abc')

        self.assert_none(result[1])
        self.assert_int(result[2][1][1])
        self.assert_float(result[2][1][2])
        self.assert_str(result[2][2])


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
        self.assertEqual(self.interpreter.execute(['quote', [1, 2, 3]]), [1, 2, 3])

    def test_quote_with_nested_lists(self):
        self.assertEqual(self.interpreter.execute(['quote', [1, 2, ['quote', [3, 4, 5]], 6]]), [1, 2, ['quote', [3, 4, 5]], 6])


if __name__ == '__main__':
    unittest.main()
