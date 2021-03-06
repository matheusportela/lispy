import unittest
from unittest.mock import patch

from lispy import *

# Disable stdout
import os
import sys
sys.stdout = open(os.devnull, 'w')


class TestLispy(unittest.TestCase):
    def setUp(self):
        self.lispy = Lispy()

    def test_t(self):
        self.assertEqual(self.lispy.eval('t'), T())

    def test_nil(self):
        self.assertEqual(self.lispy.eval('nil'), Nil())

    def test_empty_list_returns_nil(self):
        self.assertEqual(self.lispy.eval('()'), Nil())

    def test_list_function_without_args(self):
        self.assertEqual(self.lispy.eval('(list)'), Nil())

    def test_list_function_with_one_arg(self):
        self.assertEqual(self.lispy.eval('(list 1)'), [1])

    def test_list_function_with_multiple_args(self):
        self.assertEqual(self.lispy.eval('(list 1 2 3)'), [1, 2, 3])

    def test_list_evaluate_args(self):
        with self.assertRaises(Interpreter.UndefinedSymbolError):
            result = self.lispy.eval('(list 1 2 foo)')

    def test_integers_are_equal(self):
        self.assertEqual(self.lispy.eval('(= 1 1)'), T())

    def test_floats_are_equal(self):
        self.assertEqual(self.lispy.eval('(= 1.0 1.0)'), T())

    def test_strings_are_equal(self):
        self.assertEqual(self.lispy.eval('(= "abc" "abc")'), T())

    def test_integers_are_different(self):
        self.assertEqual(self.lispy.eval('(= 1 2)'), Nil())

    def test_floats_are_different(self):
        self.assertEqual(self.lispy.eval('(= 1.0 1.1)'), Nil())

    def test_strings_are_different(self):
        self.assertEqual(self.lispy.eval('(= "abc" "def")'), Nil())

    def test_sum_with_multiple_numbers(self):
        self.assertEqual(self.lispy.eval('(+ 1 2 3)'), 6)

    def test_sum_with_nested_lists(self):
        self.assertEqual(self.lispy.eval('(+ 1 2 (+ 3 4 5) (+ 6 7 8))'), 36)

    def test_sub_with_two_numbers(self):
        self.assertEqual(self.lispy.eval('(- 1 2)'), -1)

    def test_sub_with_one_number(self):
        self.assertEqual(self.lispy.eval('(- 1)'), -1)

    def test_mul_with_two_numbers(self):
        self.assertEqual(self.lispy.eval('(* 2 3)'), 6)

    def test_div_with_two_numbers(self):
        self.assertEqual(self.lispy.eval('(/ 6 3)'), 2)

    def test_power_with_two_numbers(self):
        self.assertEqual(self.lispy.eval('(pow 2 3)'), 8)

    def test_quote_does_not_evaluate_symbols(self):
        self.assertEqual(self.lispy.eval('(quote foo)'), Symbol('foo'))

    def test_quote_does_not_evaluate_lists(self):
        self.assertEqual(self.lispy.eval('(quote (1 foo))'), [Integer(1), Symbol('foo')])

    def test_set_and_get_variable_values(self):
        self.assertEqual(self.lispy.eval('(set *foo* 42)'), Nil())
        self.assertEqual(self.lispy.eval('(get *foo*)'), 42)

    def test_let_with_sum(self):
        self.assertEqual(self.lispy.eval('(let ((x 1) (y 2)) (+ x y))'), 3)

    def test_let_with_negative_sum(self):
        self.assertEqual(self.lispy.eval('(let ((x 1) (y -2)) (+ x y))'), -1)

    def test_nested_lets(self):
        self.assertEqual(self.lispy.eval('(let ((x 1)) (let ((y 2)) (+ x y)))'), 3)

    def test_let_with_same_variable_name(self):
        self.assertEqual(self.lispy.eval('(let ((x 1)) (let ((x 2)) (+ x x)))'), 4)

    def test_let_without_instructions(self):
        self.assertEqual(self.lispy.eval('(let ((x 1)))'), Nil())

    def test_let_with_multiple_instructions(self):
        self.assertEqual(self.lispy.eval('(let ((x 1) (y 2)) (+ x x) (+ x y))'), 3)

    def test_let_with_local_binding(self):
        self.assertEqual(self.lispy.eval('(let ((x 1)) (let ((x 2))) (+ x 2))'), 3)

    def test_eval_with_new_lines(self):
        self.assertEqual(self.lispy.eval('(+ 1\n2)'), 3)

    def test_write_returns_nil(self):
        self.assertEqual(self.lispy.eval('(write 1)'), Nil())

    @patch('builtins.input', return_value='abc')
    def test_read_returns_string(self, input):
        self.assertEqual(self.lispy.eval('(read)'), String('abc'))

    @patch('builtins.input', return_value='123')
    def test_read_returns_number_as_string(self, input):
        self.assertEqual(self.lispy.eval('(read)'), String('123'))

    def test_concat(self):
        self.assertEqual(self.lispy.eval('(concat "abc" "def")'), String('abcdef'))

    def test_concat_with_variables(self):
        self.assertEqual(self.lispy.eval('(let ((x "abc")) (concat x "def"))'), String('abcdef'))

    def test_defun_return_atom(self):
        self.assertEqual(self.lispy.eval('(defun foo () 1)'), Symbol('foo'))
        self.assertEqual(self.lispy.eval('(foo)'), 1)

    def test_defun_return_variable(self):
        self.assertEqual(self.lispy.eval('(defun foo (x) x)'), Symbol('foo'))
        self.assertEqual(self.lispy.eval('(foo 2)'), 2)

    def test_defun_evaluate_expression(self):
        self.assertEqual(self.lispy.eval('(defun foo (x) (+ x 1))'), Symbol('foo'))
        self.assertEqual(self.lispy.eval('(foo 2)'), 3)

    def test_defun_does_not_leak_variables(self):
        self.lispy.eval('(defun foo (x y) (- x y))')
        self.assertEqual(self.lispy.eval('(foo 5 2)'), 3)
        with self.assertRaises(Interpreter.UndefinedSymbolError):
            self.lispy.eval('(+ x y)')

    def test_function_evals_args(self):
        self.lispy.eval('(defun foo (x y) (+ x y))')
        self.assertEqual(self.lispy.eval('(foo (+ 2 3) (- 7 3))'), 9)

    def test_if_condition_true(self):
        self.assertEqual(self.lispy.eval('(if t 1 2)'), 1)

    def test_if_condition_false(self):
        self.assertEqual(self.lispy.eval('(if nil 1 2)'), 2)

    def test_if_evaluate_condition_true(self):
        self.assertEqual(self.lispy.eval('(if (= (+ 1 2) 3) 1 2)'), 1)

    def test_if_evaluate_condition_false(self):
        self.assertEqual(self.lispy.eval('(if (= (+ 1 2) 4) 1 2)'), 2)

    def test_if_evaluate_true_result(self):
        self.assertEqual(self.lispy.eval('(if t (+ 1 2) 0)'), 3)

    def test_if_evaluate_false_result(self):
        self.assertEqual(self.lispy.eval('(if nil 0 (+ 1 2))'), 3)

    def test_if_without_else_true(self):
        self.assertEqual(self.lispy.eval('(if t 1)'), 1)

    def test_if_without_else_false(self):
        self.assertEqual(self.lispy.eval('(if nil 1)'), Nil())

    def test_if_with_parameter_evaluation(self):
        self.assertEqual(self.lispy.eval('(let ((x 1)) (if t x 2))'), 1)

    def test_float_type_casting_from_int(self):
        self.assertEqual(self.lispy.eval('(float 10)'), 10.0)

    def test_float_type_casting_from_str(self):
        self.assertEqual(self.lispy.eval('(float "10")'), 10.0)

    def test_int_type_casting_from_float(self):
        self.assertEqual(self.lispy.eval('(int 10.5)'), 10)

    def test_int_type_casting_from_str(self):
        self.assertEqual(self.lispy.eval('(int "10.5")'), 10)

    def test_str_type_casting_from_int(self):
        self.assertEqual(self.lispy.eval('(str 10)'), '10')

    def test_str_type_casting_from_float(self):
        self.assertEqual(self.lispy.eval('(str 10.5)'), '10.5')

    def test_atom_nil(self):
        self.assertEqual(self.lispy.eval('(atom nil)'), T())

    def test_atom_true(self):
        self.assertEqual(self.lispy.eval('(atom t)'), T())

    def test_atom_integer(self):
        self.assertEqual(self.lispy.eval('(atom 1)'), T())

    def test_atom_float(self):
        self.assertEqual(self.lispy.eval('(atom 1.5)'), T())

    def test_atom_string(self):
        self.assertEqual(self.lispy.eval('(atom "abc")'), T())

    def test_atom_list(self):
        self.assertEqual(self.lispy.eval('(atom (list 1 2 3))'), Nil())

    def test_car_with_more_than_two_values(self):
        self.assertEqual(self.lispy.eval('(car (list 1 2 3 4 5))'), 1)

    def test_car_with_two_values(self):
        self.assertEqual(self.lispy.eval('(car (list 1 2))'), 1)

    def test_car_with_one_value(self):
        self.assertEqual(self.lispy.eval('(car (list 1))'), 1)

    def test_car_without_values(self):
        self.assertEqual(self.lispy.eval('(car (list))'), Nil())

    def test_car_with_nil(self):
        self.assertEqual(self.lispy.eval('(car ())'), Nil())

    def test_car_with_nil2(self):
        self.assertEqual(self.lispy.eval('(car nil)'), Nil())

    def test_cdr_returns_list(self):
        self.assertEqual(self.lispy.eval('(cdr (list 1 2))').__class__, List)

    def test_cdr_with_more_than_two_values(self):
        self.assertEqual(self.lispy.eval('(cdr (list 1 2 3 4 5))'), [2, 3, 4, 5])

    def test_cdr_with_two_values(self):
        self.assertEqual(self.lispy.eval('(cdr (list 1 2))'), [2])

    def test_cdr_with_one_value(self):
        self.assertEqual(self.lispy.eval('(cdr (list 1))'), Nil())

    def test_cdr_without_values(self):
        self.assertEqual(self.lispy.eval('(cdr (list))'), Nil())

    def test_cdr_with_nil(self):
        self.assertEqual(self.lispy.eval('(cdr nil)'), Nil())

    def test_cons_with_value_and_list(self):
        self.assertEqual(self.lispy.eval('(cons 1 (list 2 3))'), [1, 2, 3])

    def test_cons_with_list_and_list(self):
        self.assertEqual(self.lispy.eval('(cons (list 1 2) (list 3 4))'), [[1, 2], 3, 4])

    def test_cons_with_value_and_nil(self):
        self.assertEqual(self.lispy.eval('(cons 1 ())'), [1])

    def test_nested_cons(self):
        self.assertEqual(self.lispy.eval('(cons 1 (cons 2 (cons 3 nil)))'), [1, 2, 3])


class TestTypes(unittest.TestCase):
    def test_nil_value(self):
        self.assertEqual(Nil(), None)

    def test_nil_representation(self):
        self.assertEqual(str(Nil()), 'nil')

    def test_integer_value(self):
        self.assertEqual(Integer(1), 1)

    def test_integer_representation(self):
        self.assertEqual(str(Integer(1)), '1')

    def test_integer_type_assertion(self):
        with self.assertRaises(TypeError):
            Integer(1.0)

    def test_float_value(self):
        self.assertEqual(Float(1.0), 1.0)

    def test_float_representation(self):
        self.assertEqual(str(Float(1.0)), '1.0')

    def test_float_type_assertion(self):
        with self.assertRaises(TypeError):
            Float(1)

    def test_string_value(self):
        self.assertEqual(String('abc'), 'abc')

    def test_string_representation(self):
        self.assertEqual(str(String('abc')), 'abc')

    def test_string_type_assertion(self):
        with self.assertRaises(TypeError):
            String(1)

    def test_symbol_value(self):
        self.assertTrue(Symbol('abc') == Symbol('abc'))
        self.assertFalse(Symbol('abc') != Symbol('abc'))
        self.assertTrue(Symbol('abc') != Symbol('bcd'))
        self.assertFalse(Symbol('abc') == Symbol('bcd'))

    def test_symbol_representation(self):
        self.assertEqual(str(Symbol('abc')), ':abc')

    def test_symbol_type_assertion(self):
        with self.assertRaises(TypeError):
            Symbol(1)

    def test_list_value(self):
        self.assertEqual(List(Integer(1), Integer(2), Integer(3)), [1, 2, 3])

    def test_list_representation(self):
        self.assertEqual(str(List(Integer(1), Integer(2), Integer(3))), '(1 2 3)')

    def test_list_type_assertion(self):
        with self.assertRaises(TypeError):
            List(1)

    def test_empty_list_value(self):
        self.assertEqual(List(), [])

    def test_empty_list_representation(self):
        self.assertEqual(str(List()), '()')

    def test_list_get(self):
        l = List(Integer(1), Integer(2), Integer(3))
        self.assertEqual(l[1], 2)

    def test_list_set(self):
        l = List(Integer(1), Integer(2), Integer(3))
        l[1] = Integer(4)
        self.assertEqual(l[1], 4)

    def test_list_set_type_assertion(self):
        l = List(Integer(1), Integer(2), Integer(3))

        with self.assertRaises(TypeError):
            l[1] = 4


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

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

    def test_tokenize_with_quotes(self):
        self.assertEqual(self.lexer.tokenize('"abc def"'), ['"abc def"'])

    def test_tokenize_with_empty_list(self):
        self.assertEqual(self.lexer.tokenize('()'), [])

    def test_tokenize_list_with_one_element(self):
        self.assertEqual(self.lexer.tokenize('(nil)'), ['nil'])

    def test_tokenize_list_with_two_elements(self):
        self.assertEqual(self.lexer.tokenize('(1 2)'), ['1', '2'])

    def test_nested_lists(self):
        self.assertEqual(self.lexer.tokenize('((1 2) ((3 4) 5 6))'), [['1', '2'], [['3', '4'], '5', '6']])

    def test_raises_error_on_unbalanced_parentheses(self):
        with self.assertRaises(Lexer.InvalidInputError):
            self.lexer.tokenize('(1')


class TestParser(unittest.TestCase):
    def setUp(self):
     self.parser = Parser()

    def assert_nil(self, value):
        self.assertEqual(value, Nil())

    def assert_integer(self, value):
        self.assertEqual(value.__class__, Integer)

    def assert_float(self, value):
        self.assertEqual(value.__class__, Float)

    def assert_string(self, value):
        self.assertEqual(value.__class__, String)

    def test_empty_list(self):
        self.assertEqual(self.parser.parse([]), Nil())

    def test_first_element_is_not_parsed(self):
        self.assertEqual(self.parser.parse(['foo']), List(Symbol('foo')))

    def test_symbol(self):
        self.assertEqual(self.parser.parse(['foo', 'abc']), List(Symbol('foo'), Symbol('abc')))

    def test_nil(self):
        result = self.parser.parse(['foo', 'nil'])[1]
        self.assertEqual(result, Nil())
        self.assert_nil(result)

    def test_1_as_integer(self):
        result = self.parser.parse(['foo', '1'])[1]
        self.assertEqual(result, Integer(1))
        self.assert_integer(result)

    def test_negative_1_as_integer(self):
        result = self.parser.parse(['foo', '-1'])[1]
        self.assertEqual(result, Integer(-1))
        self.assert_integer(result)

    def test_1_1_as_float(self):
        result = self.parser.parse(['foo', '1.1'])[1]
        self.assertEqual(result, Float(1.1))
        self.assert_float(result)

    def test_0_1_as_float(self):
        result = self.parser.parse(['foo', '.1'])[1]
        self.assertEqual(result, Float(0.1))
        self.assert_float(result)

    def test_negative_1_1_as_float(self):
        result = self.parser.parse(['foo', '-1.1'])[1]
        self.assertEqual(result, Float(-1.1))
        self.assert_float(result)

    def test_a_as_string(self):
        result = self.parser.parse(['foo', '"a"'])[1]
        self.assertEqual(result, String('a'))
        self.assert_string(result)

    def test_abc_as_string(self):
        result = self.parser.parse(['foo', '"abc"'])[1]
        self.assertEqual(result, String('abc'))
        self.assert_string(result)

    def test_abc_def_as_string(self):
        result = self.parser.parse(['foo', '"abc def"'])[1]
        self.assertEqual(result, String('abc def'))
        self.assert_string(result)

    def test_nested_lists(self):
        result = self.parser.parse(['foo', 'nil', ['foo', ['foo', '2', '3.0'], '"abc"']])

        self.assertEqual(result[1], Nil())
        self.assertEqual(result[2][1][1], Integer(2))
        self.assertEqual(result[2][1][2], Float(3.0))
        self.assertEqual(result[2][2], String('abc'))

        self.assert_nil(result[1])
        self.assert_integer(result[2][1][1])
        self.assert_float(result[2][1][2])
        self.assert_string(result[2][2])


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def test_raises_error_on_unknown_function(self):
        with self.assertRaises(Interpreter.UndefinedFunctionError):
            self.interpreter.execute(
                List(
                    Symbol('abc'),
                    Integer(1),
                    Integer(2)))

    def test_sum_two_ints(self):
        self.assertEqual(
            self.interpreter.execute(
                List(
                    Symbol('+'),
                    Integer(1),
                    Integer(2))),
                Integer(3))

    def test_sum_two_floats(self):
        self.assertEqual(
            self.interpreter.execute(
                List(
                    Symbol('+'),
                    Float(1.0),
                    Float(1.5))),
                Float(2.5))

    def test_sum_multiple_ints_and_floats(self):
        self.assertEqual(
            self.interpreter.execute(
                List(
                    Symbol('+'),
                    Integer(1),
                    Float(2.5),
                    Integer(-3),
                    Float(-1.25))),
                Float(-0.75))

    def test_quote_return_same_list(self):
        self.assertEqual(
            self.interpreter.execute(
                List(
                    Symbol('quote'),
                    List(
                        Integer(1),
                        Integer(2),
                        Integer(3)))),
                List(
                    Integer(1),
                    Integer(2),
                    Integer(3)))

    def test_quote_with_nested_lists(self):
        self.assertEqual(
            self.interpreter.execute(
                List(
                    Symbol('quote'),
                    List(
                        Integer(1),
                        Integer(2),
                        List(
                            Symbol('quote'),
                            List(
                                Integer(3),
                                Integer(4), Integer(5))),
                        Integer(6)))),
                List(
                    Integer(1),
                    Integer(2),
                    List(
                        Symbol('quote'),
                        List(
                            Integer(3),
                            Integer(4),
                            Integer(5))),
                    Integer(6)))


if __name__ == '__main__':
    unittest.main()
