# lispy
Didactic Lisp interpreter in Python

## Usage

```shell
$ python lispy.py
lispy v0.0.1

>>> (quote 1 2 3)
(1 2 3)
>>> (+ 1 2 3)
6
>>> (+ 1 2 (+ 3 4) 5)
15
```

## Test

```shell
$ python test_lispy.py
```

## Standard Library
`quote`: Avoid evaluation of the given argument
```lisp
>>> (quote foo)
foo
>>> (quote (1 2 foo))
(1 2 foo)
```

`list`: Create list evaluating the given arguments
```lisp
>>> (list 1)
(1)
>>> (list 1 2 3)
(1 2 3)
```

`set`: Set value to global variable
```lisp
>>> (set (quote *foo*) 42)
nil
```

`get`: Get value from previous defined global variable
```lisp
>>> (set (quote *foo*) 42)
nil
>>> (get (quote *foo*))
42
```

`+` or `sum`: Sum all arguments
```lisp
>>> (+ 1 2 3)
6
>>> (sum 1 2 (+ 3 4) 5)
15
```
