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
`quote`: Define a new list
```lisp
>>> (quote 1 2 3)
(1 2 3)
```

`+` or `sum`: Sum all arguments
```lisp
>>> (+ 1 2 3)
6
>>> (sum 1 2 (+ 3 4) 5)
15
```
